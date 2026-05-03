from pydantic import BaseModel, Field
from typing import List, Dict

class SkillGapRequest(BaseModel):
    resume_text: str = Field(..., min_length=10, max_length=5000)
    target_role: str = Field(..., min_length=2, max_length=100)
    target_country: str = Field(default="USA", max_length=50)

class SkillScore(BaseModel):
    skill: str
    user_score: int    # 0-100
    industry_score: int

class SkillGapResponse(BaseModel):
    radar_data: List[SkillScore]
    matched_skills: List[str]
    missing_skills: List[str]
    overall_match: int  # 0-100
    top_recommendation: str
