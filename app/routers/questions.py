from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.question import QuestionGenerateRequest, QuestionResponse, QuestionListResponse
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.question import Question
from app.services.question_service import generate_questions

router = APIRouter(prefix="/api/questions", tags=["智能出题"])


@router.post("/generate", response_model=list[QuestionResponse])
async def generate(data: QuestionGenerateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        questions = await generate_questions(
            db=db,
            user_id=current_user.id,
            subject=data.subject,
            knowledge_point=data.knowledge_point,
            difficulty=data.difficulty,
            question_type=data.question_type,
            count=data.count,
            random_mode=data.random_mode,
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"调用AI服务失败: {str(e)}")

    return [QuestionResponse.model_validate(q) for q in questions]


@router.get("", response_model=QuestionListResponse)
def list_questions(
    page: int = 1,
    page_size: int = 10,
    subject: str | None = None,
    difficulty: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Question).filter(Question.user_id == current_user.id)
    if subject:
        q = q.filter(Question.subject == subject)
    if difficulty:
        q = q.filter(Question.difficulty == difficulty)

    total = q.count()
    items = q.order_by(Question.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return QuestionListResponse(
        items=[QuestionResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(question_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id, Question.user_id == current_user.id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    return QuestionResponse.model_validate(question)


@router.delete("/{question_id}", status_code=204)
def delete_question(question_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id, Question.user_id == current_user.id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    db.delete(question)
    db.commit()
