from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import re

VALID_INTENTS = {"answer", "help", "navigation"}

class ChatMessage(BaseModel):
    role: str = Field(..., max_length=20)
    content: str = Field(..., max_length=4000)

class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=100)
    topic_id: str = Field(..., min_length=1, max_length=50)
    message: str = Field(..., max_length=2000)
    current_question: str = Field(..., max_length=500)
    intent: str = Field(default="answer", max_length=20)
    chat_history: List[ChatMessage] = Field(default=[], max_length=30)

    @field_validator("intent")
    @classmethod
    def validate_intent(cls, v):
        if v not in VALID_INTENTS:
            return "answer"
        return v

    @field_validator("session_id")
    @classmethod
    def sanitize_session_id(cls, v):
        # Only allow alphanumeric, dash, underscore
        if not re.match(r'^[\w-]+$', v):
            raise ValueError("Invalid session_id format")
        return v

class ChatResponse(BaseModel):
    message: str
    tip: Optional[str] = None
    confidence_score: Optional[int] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    suggested_improvement: Optional[str] = None
    topic_progress: int
    is_topic_complete: bool
