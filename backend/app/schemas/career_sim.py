from pydantic import BaseModel, Field
from typing import List

class CareerSimRequest(BaseModel):
    gpa: float = Field(..., ge=0.0, le=4.0)
    field_of_study: str = Field(..., max_length=100)
    target_country: str = Field(..., max_length=50)
    work_experience_years: int = Field(default=0, ge=0, le=10)
    program_duration_years: int = Field(default=2, ge=1, le=4)
    annual_tuition_usd: float = Field(..., ge=0)
    monthly_living_usd: float = Field(default=1500, ge=0)
    target_role: str = Field(default="Data Scientist", max_length=100)
    skills_text: str = Field(default="", max_length=2000)

class YearProjection(BaseModel):
    year: int
    salary: float
    cumulative_earnings: float
    cumulative_cost: float
    net_position: float

class CareerSimResponse(BaseModel):
    predicted_starting_salary: float
    salary_at_5yr: float
    salary_at_10yr: float
    total_investment: float
    break_even_years: float
    ten_year_net: float
    roi_percent: float
    demand_index: float          # 0-100 job market demand score
    career_grade: str            # A+, A, B+, B, C
    projections: List[YearProjection]
    top_skills_to_add: List[str]
    summary: str
