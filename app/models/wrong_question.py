from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from app.database import Base


class WrongQuestion(Base):
    __tablename__ = "wrong_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=True)
    subject = Column(String(30), nullable=False)
    knowledge_point = Column(String(100), nullable=False)
    question_content = Column(Text, nullable=False)  # JSON: 存题目内容快照
    wrong_count = Column(Integer, default=1)
    note = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
