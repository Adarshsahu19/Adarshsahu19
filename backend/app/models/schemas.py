from datetime import datetime
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=4)
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    created_at: datetime


class SessionResponse(BaseModel):
    session_id: str
    created_at: datetime


class VoiceMessage(BaseModel):
    session_id: str
    transcript: str


class HealthResponse(BaseModel):
    status: str = 'ok'
