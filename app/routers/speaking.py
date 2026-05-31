import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.speaking import (
    SessionCreateRequest, ChatRequest,
    SessionResponse, SessionDetailResponse, SessionListResponse,
    MessageResponse,
)
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.speaking import SpeakingSession, SpeakingMessage
from app.services.speaking_service import chat_stream, create_session

router = APIRouter(prefix="/api/speaking", tags=["口语陪练"])


@router.post("/sessions", response_model=SessionResponse)
def new_session(data: SessionCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = create_session(
        db=db,
        user_id=current_user.id,
        scenario=data.scenario,
        role=data.role,
        title=data.title,
        language=data.language,
    )
    return SessionResponse.model_validate(session)


@router.get("/sessions", response_model=SessionListResponse)
def list_sessions(
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(SpeakingSession).filter(SpeakingSession.user_id == current_user.id)
    total = q.count()
    items = q.order_by(SpeakingSession.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return SessionListResponse(
        items=[SessionResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
def get_session(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(SpeakingSession).filter(
        SpeakingSession.id == session_id, SpeakingSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    messages = (
        db.query(SpeakingMessage)
        .filter(SpeakingMessage.session_id == session_id)
        .order_by(SpeakingMessage.created_at.asc())
        .all()
    )

    resp = SessionDetailResponse.model_validate(session)
    resp.messages = [MessageResponse.model_validate(m) for m in messages]
    return resp


@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(SpeakingSession).filter(
        SpeakingSession.id == session_id, SpeakingSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    db.delete(session)
    db.commit()


@router.post("/sessions/{session_id}/chat")
async def chat(
    session_id: int,
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not data.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")

    async def event_generator():
        async for event in chat_stream(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
            user_message=data.message,
        ):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
