from pydantic import BaseModel
from datetime import datetime


class WrongQuestionAdd(BaseModel):
    subject: str
    knowledge_point: str
    question_content: str  # JSON


class WrongQuestionResponse(BaseModel):
    id: int
    subject: str
    knowledge_point: str
    question_content: str
    wrong_count: int
    note: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WrongQuestionListResponse(BaseModel):
    items: list[WrongQuestionResponse]
    total: int
    page: int
    page_size: int
