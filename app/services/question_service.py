import json
import re
from sqlalchemy.orm import Session
from app.services.deepseek_client import chat_completion
from app.prompts.question_prompts import build_question_prompt
from app.models.question import Question


MAX_RETRIES = 2


def _clean_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text


def _parse_questions(raw: str) -> list[dict]:
    data = json.loads(_clean_json(raw))
    return data.get("questions", [])


async def generate_questions(
    db: Session,
    user_id: int,
    subject: str,
    knowledge_point: str,
    difficulty: str,
    question_type: str,
    count: int,
    random_mode: bool = False,
) -> list[Question]:
    messages = build_question_prompt(subject, knowledge_point, difficulty, question_type, count, random_mode)

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = await chat_completion(
                messages,
                temperature=0.8,
                max_tokens=4096,
                response_format={"type": "json_object"},
            )
            raw = resp["choices"][0]["message"]["content"]
            questions_data = _parse_questions(raw)
            break
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                messages.append({
                    "role": "user",
                    "content": "请严格按照JSON格式重新输出，不要包含代码块标记。"
                })
    else:
        raise ValueError(f"AI响应解析失败，请重试: {last_error}")

    saved = []
    for q in questions_data:
        question = Question(
            user_id=user_id,
            subject=subject,
            knowledge_point=knowledge_point,
            difficulty=difficulty,
            question_type=q.get("type", question_type),
            content=json.dumps(q, ensure_ascii=False),
        )
        db.add(question)
        saved.append(question)

    db.commit()
    for q in saved:
        db.refresh(q)
    return saved
