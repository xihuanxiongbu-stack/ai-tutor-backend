from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EssayGradeRequest(BaseModel):
    title: str = ""
    topic: str = ""
    content: str
    language: str = "zh"


class EssayFeedbackResponse(BaseModel):
    id: int
    overall_score: int
    grammar_score: int
    content_score: int
    structure_score: int
    corrections: str
    suggestions: str
    improved_essay: str
    feedback_summary: str

    model_config = {"from_attributes": True}


class EssayResponse(BaseModel):
    id: int
    title: str
    topic: str
    content: str
    word_count: int
    language: str
    created_at: datetime
    feedback: Optional[EssayFeedbackResponse] = None

    model_config = {"from_attributes": True}


class EssayListResponse(BaseModel):
    items: list[EssayResponse]
    total: int
    page: int
    page_size: int
