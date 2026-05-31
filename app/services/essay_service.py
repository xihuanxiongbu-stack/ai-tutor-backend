import json
import re
import logging
from sqlalchemy.orm import Session
from app.services.deepseek_client import chat_completion_stream
from app.prompts.essay_prompts import build_essay_prompt
from app.models.essay import EssaySubmission, EssayFeedback

logger = logging.getLogger(__name__)

MAX_RETRIES = 2


def _clean_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text


async def grade_essay_stream(
    db: Session,
    user_id: int,
    title: str,
    topic: str,
    content: str,
    language: str,
):
    word_count = len(content)
    essay = EssaySubmission(
        user_id=user_id,
        title=title,
        topic=topic,
        content=content,
        word_count=word_count,
        language=language,
    )
    db.add(essay)
    db.commit()
    db.refresh(essay)
    yield {"type": "essay_created", "essay_id": essay.id}

    messages = build_essay_prompt(title, topic, content, language)
    full_response = ""

    try:
        async for chunk in chat_completion_stream(messages, temperature=0.3, max_tokens=4096):
            full_response += chunk
            yield {"type": "chunk", "content": chunk}

        data = json.loads(_clean_json(full_response))

        feedback = EssayFeedback(
            essay_id=essay.id,
            overall_score=data.get("overall_score", 0),
            grammar_score=data.get("grammar_score", 0),
            content_score=data.get("content_score", 0),
            structure_score=data.get("structure_score", 0),
            corrections=json.dumps(data.get("corrections", []), ensure_ascii=False),
            suggestions=json.dumps(data.get("suggestions", []), ensure_ascii=False),
            improved_essay=data.get("improved_essay", ""),
            feedback_summary=data.get("feedback_summary", ""),
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)

        yield {
            "type": "result",
            "data": {
                "essay_id": essay.id,
                "overall_score": feedback.overall_score,
                "grammar_score": feedback.grammar_score,
                "content_score": feedback.content_score,
                "structure_score": feedback.structure_score,
                "corrections": feedback.corrections,
                "suggestions": feedback.suggestions,
                "improved_essay": feedback.improved_essay,
                "feedback_summary": feedback.feedback_summary,
            },
        }
    except Exception as e:
        logger.error(f"Essay grading failed: {e}")
        yield {"type": "error", "message": f"批改失败: {str(e)}"}

    yield {"type": "done"}
