from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from app.database import Base


class EssaySubmission(Base):
    __tablename__ = "essay_submissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), default="")
    topic = Column(String(200), default="")
    content = Column(Text, nullable=False)
    word_count = Column(Integer, default=0)
    language = Column(String(10), default="zh")
    created_at = Column(DateTime, server_default=func.now())


class EssayFeedback(Base):
    __tablename__ = "essay_feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    essay_id = Column(Integer, ForeignKey("essay_submissions.id", ondelete="CASCADE"), unique=True, nullable=False)
    overall_score = Column(Integer, default=0)
    grammar_score = Column(Integer, default=0)
    content_score = Column(Integer, default=0)
    structure_score = Column(Integer, default=0)
    corrections = Column(Text, default="[]")
    suggestions = Column(Text, default="[]")
    improved_essay = Column(Text, default="")
    feedback_summary = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())
