from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from app.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String(30), nullable=False)
    knowledge_point = Column(String(100), nullable=False)
    difficulty = Column(String(10), nullable=False)
    question_type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, server_default=func.now())
