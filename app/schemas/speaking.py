from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SessionCreateRequest(BaseModel):
    scenario: str
    role: str
    title: str = ""
    language: str = "en"


class ChatRequest(BaseModel):
    message: str


class SessionResponse(BaseModel):
    id: int
    title: str
    scenario: str
    role: str
    language: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    feedback: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionDetailResponse(BaseModel):
    id: int
    title: str
    scenario: str
    role: str
    language: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []

    model_config = {"from_attributes": True}


class SessionListResponse(BaseModel):
    items: list[SessionResponse]
    total: int
    page: int
    page_size: int
