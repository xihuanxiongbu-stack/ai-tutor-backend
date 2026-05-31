from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.wrong_question import WrongQuestionAdd, WrongQuestionResponse, WrongQuestionListResponse
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.wrong_question import WrongQuestion

router = APIRouter(prefix="/api/wrong-book", tags=["错题库"])


@router.post("/add", response_model=WrongQuestionResponse)
def add_wrong(data: WrongQuestionAdd, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 检查是否已存在（同样内容不重复添加）
    existing = db.query(WrongQuestion).filter(
        WrongQuestion.user_id == current_user.id,
        WrongQuestion.question_content == data.question_content,
    ).first()
    if existing:
        existing.wrong_count += 1
        db.commit()
        db.refresh(existing)
        return WrongQuestionResponse.model_validate(existing)

    wq = WrongQuestion(
        user_id=current_user.id,
        subject=data.subject,
        knowledge_point=data.knowledge_point,
        question_content=data.question_content,
    )
    db.add(wq)
    db.commit()
    db.refresh(wq)
    return WrongQuestionResponse.model_validate(wq)


@router.get("", response_model=WrongQuestionListResponse)
def list_wrong(
    page: int = 1,
    page_size: int = 20,
    subject: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(WrongQuestion).filter(WrongQuestion.user_id == current_user.id)
    if subject:
        q = q.filter(WrongQuestion.subject == subject)
    total = q.count()
    items = q.order_by(WrongQuestion.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return WrongQuestionListResponse(
        items=[WrongQuestionResponse.model_validate(item) for item in items],
        total=total, page=page, page_size=page_size,
    )


@router.delete("/{wrong_id}", status_code=204)
def delete_wrong(wrong_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wq = db.query(WrongQuestion).filter(
        WrongQuestion.id == wrong_id, WrongQuestion.user_id == current_user.id
    ).first()
    if not wq:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(wq)
    db.commit()


@router.delete("/clear/all", status_code=204)
def clear_all(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(WrongQuestion).filter(WrongQuestion.user_id == current_user.id).delete()
    db.commit()
