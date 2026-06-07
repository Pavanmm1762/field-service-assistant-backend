from pydantic import BaseModel
from typing import List


class SessionSummary(BaseModel):
    session_id: str
    equipment: str
    issue: str
    severity: str
    confidence: int
    image_path: str
    status: str
    created_at: str


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: str


class SessionDetail(BaseModel):
    session_id: str
    analysis: dict
    messages: List[ChatMessage]