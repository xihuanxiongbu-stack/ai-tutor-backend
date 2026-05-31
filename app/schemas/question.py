from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class QuestionGenerateRequest(BaseModel):
    subject: str
    knowledge_point: str
    difficulty: str  # 简单/中等/困难
    question_type: str  # 选择题/填空题/简答题
    count: int = 1
    random_mode: bool = False


class QuestionResponse(BaseModel):
    id: int
    subject: str
    knowledge_point: str
    difficulty: str
    question_type: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class QuestionListResponse(BaseModel):
    items: list[QuestionResponse]
    total: int
    page: int
    page_size: int
