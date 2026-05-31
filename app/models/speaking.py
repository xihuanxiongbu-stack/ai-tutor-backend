from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from app.database import Base


class SpeakingSession(Base):
    __tablename__ = "speaking_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), default="")
    scenario = Column(String(50), nullable=False)
    role = Column(String(50), nullable=False)
    language = Column(String(10), default="en")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class SpeakingMessage(Base):
    __tablename__ = "speaking_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("speaking_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    feedback = Column(Text, default="null")
    created_at = Column(DateTime, server_default=func.now())
