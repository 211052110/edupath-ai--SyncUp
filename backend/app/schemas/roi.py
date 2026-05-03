from pydantic import BaseModel, Field
from typing import List

class ROIRequest(BaseModel):
    duration_years: int = Field(..., ge=1, le=10)
    annual_tuition: int = Field(..., ge=0)
    monthly_living_costs: int = Field(..., ge=0)
    target_country: str = Field(..., max_length=50)
    field_of_study: str = Field(..., max_length=100)
    expected_salary: int = Field(..., ge=0, le=10_000_000)

class ProjectionData(BaseModel):
    year: str
    cost: int
    earnings: int

class ROIMetrics(BaseModel):
    total_investment: int
    ten_year_earnings: int
    ten_year_roi_percentage: int
    break_even_year: float
    monthly_emi: int
    loan_duration_years: int

class ROIInsights(BaseModel):
    insight_text: str
    recommendation: str
    comparison: str

class ROIResponse(BaseModel):
    metrics: ROIMetrics
    insights: ROIInsights
    projection_data: List[ProjectionData]
