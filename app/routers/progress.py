from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.question import Question
from app.models.essay import EssaySubmission, EssayFeedback
from app.models.speaking import SpeakingSession, SpeakingMessage

router = APIRouter(prefix="/api/progress", tags=["学习统计"])


@router.get("")
def get_progress(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    question_count = db.query(func.count(Question.id)).filter(Question.user_id == current_user.id).scalar()
    essay_count = db.query(func.count(EssaySubmission.id)).filter(EssaySubmission.user_id == current_user.id).scalar()
    session_count = db.query(func.count(SpeakingSession.id)).filter(SpeakingSession.user_id == current_user.id).scalar()

    avg_score = (
        db.query(func.avg(EssayFeedback.overall_score))
        .join(EssaySubmission, EssayFeedback.essay_id == EssaySubmission.id)
        .filter(EssaySubmission.user_id == current_user.id)
        .scalar()
    ) or 0

    recent_questions = (
        db.query(Question)
        .filter(Question.user_id == current_user.id)
        .order_by(Question.created_at.desc())
        .limit(5)
        .all()
    )

    recent_essays = (
        db.query(EssaySubmission)
        .filter(EssaySubmission.user_id == current_user.id)
        .order_by(EssaySubmission.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "stats": {
            "question_count": question_count,
            "essay_count": essay_count,
            "session_count": session_count,
            "avg_essay_score": round(float(avg_score), 1),
        },
        "recent_questions": [
            {
                "id": q.id,
                "subject": q.subject,
                "knowledge_point": q.knowledge_point,
                "difficulty": q.difficulty,
                "question_type": q.question_type,
                "created_at": q.created_at.isoformat(),
            }
            for q in recent_questions
        ],
        "recent_essays": [
            {
                "id": e.id,
                "title": e.title,
                "topic": e.topic,
                "language": e.language,
                "created_at": e.created_at.isoformat(),
            }
            for e in recent_essays
        ],
    }
