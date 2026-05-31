import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.essay import EssayGradeRequest, EssayResponse, EssayListResponse, EssayFeedbackResponse
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.essay import EssaySubmission, EssayFeedback
from app.services.essay_service import grade_essay_stream

router = APIRouter(prefix="/api/essays", tags=["作文批改"])


@router.post("/grade")
async def grade(data: EssayGradeRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not data.content.strip():
        raise HTTPException(status_code=400, detail="作文内容不能为空")
    if len(data.content) > 10000:
        raise HTTPException(status_code=400, detail="作文内容不能超过10000字")

    async def event_generator():
        async for event in grade_essay_stream(
            db=db,
            user_id=current_user.id,
            title=data.title,
            topic=data.topic,
            content=data.content,
            language=data.language,
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


@router.get("", response_model=EssayListResponse)
def list_essays(
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(EssaySubmission).filter(EssaySubmission.user_id == current_user.id)
    total = q.count()
    items = q.order_by(EssaySubmission.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    results = []
    for essay in items:
        feedback = db.query(EssayFeedback).filter(EssayFeedback.essay_id == essay.id).first()
        essay_resp = EssayResponse.model_validate(essay)
        if feedback:
            essay_resp.feedback = EssayFeedbackResponse.model_validate(feedback)
        results.append(essay_resp)

    return EssayListResponse(items=results, total=total, page=page, page_size=page_size)


@router.get("/{essay_id}", response_model=EssayResponse)
def get_essay(essay_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    essay = db.query(EssaySubmission).filter(
        EssaySubmission.id == essay_id, EssaySubmission.user_id == current_user.id
    ).first()
    if not essay:
        raise HTTPException(status_code=404, detail="作文不存在")

    feedback = db.query(EssayFeedback).filter(EssayFeedback.essay_id == essay.id).first()
    resp = EssayResponse.model_validate(essay)
    if feedback:
        resp.feedback = EssayFeedbackResponse.model_validate(feedback)
    return resp


@router.delete("/{essay_id}", status_code=204)
def delete_essay(essay_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    essay = db.query(EssaySubmission).filter(
        EssaySubmission.id == essay_id, EssaySubmission.user_id == current_user.id
    ).first()
    if not essay:
        raise HTTPException(status_code=404, detail="作文不存在")
    db.delete(essay)
    db.commit()
