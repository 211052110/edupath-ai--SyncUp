from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class LenderRecommendation(BaseModel):
    name: str
    interest_rate: str
    max_amount: str
    processing_time: str

class LoanScoreRequest(BaseModel):
    gpa: float = Field(..., ge=0.0, le=4.0)
    annual_budget: int = Field(..., ge=0)
    target_country: str = Field(..., max_length=50)
    work_experience_years: int = Field(..., ge=0)
    english_score: float = Field(..., ge=0.0, le=9.0)

class LoanScoreResponse(BaseModel):
    overall_score: int
    classification: str
    explanation: str
    risk_level: str
    improvement_suggestions: List[str]
    factors: Dict[str, int]
    recommended_lenders: List[LenderRecommendation]
    model_info: Optional[Dict] = None   # e.g. {"model": "LightGBM", "cv_auc": 0.972}
