import json
import re
import logging
from sqlalchemy.orm import Session
from app.services.deepseek_client import chat_completion_stream
from app.prompts.speaking_prompts import build_speaking_prompt
from app.models.speaking import SpeakingSession, SpeakingMessage

logger = logging.getLogger(__name__)


def _clean_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text


async def chat_stream(
    db: Session,
    session_id: int,
    user_id: int,
    user_message: str,
):
    session = db.query(SpeakingSession).filter(
        SpeakingSession.id == session_id,
        SpeakingSession.user_id == user_id,
    ).first()
    if not session:
        yield {"type": "error", "message": "会话不存在"}
        return

    user_msg = SpeakingMessage(
        session_id=session_id,
        role="user",
        content=user_message,
    )
    db.add(user_msg)
    db.commit()

    previous = (
        db.query(SpeakingMessage)
        .filter(SpeakingMessage.session_id == session_id)
        .order_by(SpeakingMessage.created_at.asc())
        .all()
    )
    history = []
    for m in previous[:-1]:
        history.append({"role": m.role, "content": m.content})

    messages = build_speaking_prompt(
        scenario=session.scenario,
        role=session.role,
        language=session.language,
        history=history,
    )

    full_response = ""
    try:
        async for chunk in chat_completion_stream(messages, temperature=0.7, max_tokens=2048):
            full_response += chunk
            yield {"type": "chunk", "content": chunk}

        data = json.loads(_clean_json(full_response))
        ai_message_text = data.get("message", full_response)
        feedback = data.get("feedback", {})

        ai_msg = SpeakingMessage(
            session_id=session_id,
            role="assistant",
            content=ai_message_text,
            feedback=json.dumps(feedback, ensure_ascii=False),
        )
        db.add(ai_msg)
        db.commit()
        db.refresh(ai_msg)

        yield {
            "type": "message",
            "message_id": ai_msg.id,
            "content": ai_message_text,
            "feedback": feedback,
        }
    except Exception as e:
        logger.error(f"Speaking chat failed: {e}")
        yield {"type": "error", "message": f"对话生成失败: {str(e)}"}

    yield {"type": "done"}


def create_session(db: Session, user_id: int, scenario: str, role: str, title: str = "", language: str = "en") -> SpeakingSession:
    session = SpeakingSession(
        user_id=user_id,
        title=title or f"{scenario} - {role}",
        scenario=scenario,
        role=role,
        language=language,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session
