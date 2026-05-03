from pydantic import BaseModel, Field
from typing import List

class UniversityQARequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)

class UniversityQAResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: str  # "high" | "medium" | "low"
