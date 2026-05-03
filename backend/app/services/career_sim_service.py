"""
Career Simulator Service
- XGBoost salary prediction (reuses roi model)
- Career Demand Index per country/field/role
- 10-year financial projection with growth curve
- Skill gap quick-check for top skills to add
- No external API needed — fully local
"""

import numpy as np
import logging
from app.schemas.career_sim import CareerSimRequest, CareerSimResponse, YearProjection
from app.core.model_loader import get_roi_model

logger = logging.getLogger("edupath.career_sim")

# ── Encodings (must match train_models.py) ────────────────────────────────────
COUNTRY_ENC = {
    "usa": 0, "united states": 0,
    "germany": 1,
    "uk": 2, "united kingdom": 2, "england": 2,
    "canada": 3,
    "australia": 4,
}
FIELD_ENC = {
    "computer science": 0, "cs": 0, "software": 0,
    "data science": 1, "data": 1,
    "ai": 2, "artificial intelligence": 2, "machine learning": 2, "ml": 2,
    "business": 3, "mba": 3, "management": 3,
    "finance": 4, "accounting": 4,
}

# ── Demand Index: (country, role_keyword) → score 0-100 ──────────────────────
DEMAND_DATA = {
    # USA
    ("usa", "data scientist"):       92, ("usa", "ml engineer"):        95,
    ("usa", "software engineer"):    90, ("usa", "ai researcher"):       88,
    ("usa", "data analyst"):         82, ("usa", "full stack"):          85,
    # Germany
    ("germany", "data scientist"):   80, ("germany", "ml engineer"):     82,
    ("germany", "software engineer"):85, ("germany", "ai researcher"):   78,
    ("germany", "data analyst"):     75, ("germany", "full stack"):      80,
    # UK
    ("uk", "data scientist"):        84, ("uk", "ml engineer"):          86,
    ("uk", "software engineer"):     88, ("uk", "ai researcher"):        80,
    ("uk", "data analyst"):          79, ("uk", "full stack"):           83,
    # Canada
    ("canada", "data scientist"):    86, ("canada", "ml engineer"):      88,
    ("canada", "software engineer"): 87, ("canada", "ai researcher"):    82,
    ("canada", "data analyst"):      80, ("canada", "full stack"):       84,
    # Australia
    ("australia", "data scientist"): 78, ("australia", "ml engineer"):   80,
    ("australia", "software engineer"):82,("australia","ai researcher"):  74,
    ("australia", "data analyst"):   76, ("australia", "full stack"):    79,
}

# Role → annual salary growth rate
GROWTH_RATES = {
    "data scientist": 0.07, "ml engineer": 0.08, "ai researcher": 0.07,
    "software engineer": 0.065, "data analyst": 0.055, "full stack": 0.06,
}
DEFAULT_GROWTH = 0.065

# Top skills by country/field combo
TOP_SKILLS = {
    ("usa", "ai"):              ["PyTorch", "LLM fine-tuning", "MLOps", "CUDA"],
    ("usa", "data science"):    ["dbt", "Spark", "Snowflake", "Airflow"],
    ("usa", "computer science"):["Kubernetes", "System Design", "Rust", "AWS"],
    ("germany", "computer science"):["C++", "ROS", "Embedded", "AUTOSAR"],
    ("germany", "data science"):["Apache Flink", "Kafka", "Scala"],
    ("uk", "data science"):     ["Power BI", "Azure ML", "PySpark"],
    ("canada", "computer science"):["React Native", "AWS", "Terraform"],
    ("australia", "data science"):["Tableau", "Azure", "SQL tuning"],
}
DEFAULT_SKILLS = ["Docker", "Cloud (AWS/GCP/Azure)", "SQL", "Communication"]


def _encode(mapping: dict, value: str, default: int = 0) -> int:
    vl = value.lower()
    for k, v in mapping.items():
        if k in vl:
            return v
    return default


def _demand_index(country: str, role: str) -> float:
    cl, rl = country.lower(), role.lower()
    country_key = next((k for k in ["usa", "germany", "uk", "canada", "australia"] if k in cl), "usa")
    role_key = next((k for k in ["data scientist", "ml engineer", "software engineer",
                                  "ai researcher", "data analyst", "full stack"] if k in rl), "software engineer")
    return float(DEMAND_DATA.get((country_key, role_key), 75))


def _growth_rate(role: str) -> float:
    rl = role.lower()
    for k, v in GROWTH_RATES.items():
        if k in rl:
            return v
    return DEFAULT_GROWTH


def _top_skills(country: str, field: str) -> list[str]:
    cl = country.lower()
    fl = field.lower()
    country_key = next((k for k in ["usa", "germany", "uk", "canada", "australia"] if k in cl), "usa")
    field_key = next((k for k in ["ai", "data science", "computer science"] if k in fl), "computer science")
    return TOP_SKILLS.get((country_key, field_key), DEFAULT_SKILLS)


def _career_grade(roi: float, demand: float, salary: float) -> str:
    score = roi * 0.4 + demand * 0.3 + min(100, salary / 1500) * 0.3
    if score >= 85:   return "A+"
    elif score >= 75: return "A"
    elif score >= 62: return "B+"
    elif score >= 50: return "B"
    else:             return "C"


def simulate_career(data: CareerSimRequest) -> CareerSimResponse:
    # ── Salary prediction via XGBoost ─────────────────────────────────────────
    try:
        model = get_roi_model()
        gpa_n   = (data.gpa / 4.0) * 100
        tui_n   = min(100, (data.annual_tuition_usd / 80000) * 100)
        liv_n   = min(100, (data.monthly_living_usd / 3000) * 100)
        work_n  = data.work_experience_years * 14
        c_enc   = _encode(COUNTRY_ENC, data.target_country)
        f_enc   = _encode(FIELD_ENC, data.field_of_study)
        X = np.array([[gpa_n, data.program_duration_years, tui_n, liv_n, c_enc, f_enc, work_n]])
        starting_salary = float(model.predict(X)[0])
    except Exception as e:
        logger.warning(f"Model predict failed, using fallback: {e}")
        starting_salary = 85000.0

    # ── Costs ─────────────────────────────────────────────────────────────────
    annual_living = data.monthly_living_usd * 12
    total_investment = (data.annual_tuition_usd + annual_living) * data.program_duration_years

    # ── Growth & projections ──────────────────────────────────────────────────
    growth = _growth_rate(data.target_role)
    projections = []
    cum_earnings = 0.0
    cum_cost = total_investment
    break_even = None

    for yr in range(1, 11):
        salary_yr = starting_salary * ((1 + growth) ** (yr - 1))
        cum_earnings += salary_yr
        net = cum_earnings - cum_cost
        if break_even is None and net >= 0:
            break_even = float(yr)
        projections.append(YearProjection(
            year=yr,
            salary=round(salary_yr, 0),
            cumulative_earnings=round(cum_earnings, 0),
            cumulative_cost=round(cum_cost, 0),
            net_position=round(net, 0),
        ))

    if break_even is None:
        break_even = round(total_investment / max(starting_salary, 1) + data.program_duration_years, 1)

    sal_5yr  = starting_salary * ((1 + growth) ** 4)
    sal_10yr = starting_salary * ((1 + growth) ** 9)
    ten_yr_earnings = sum(p.salary for p in projections)
    ten_yr_net = ten_yr_earnings - total_investment
    roi_pct = round((ten_yr_net / max(total_investment, 1)) * 100, 1)

    demand = _demand_index(data.target_country, data.target_role)
    grade  = _career_grade(min(100, roi_pct / 10), demand, starting_salary / 1000)
    skills = _top_skills(data.target_country, data.field_of_study)

    summary = (
        f"As a {data.target_role} in {data.target_country}, "
        f"you're projected to start at ${starting_salary:,.0f}/yr, "
        f"reaching ${sal_5yr:,.0f} by year 5. "
        f"Break-even on your ${total_investment:,.0f} investment in ~{break_even:.1f} years. "
        f"10-year net gain: ${ten_yr_net:,.0f} ({roi_pct:.0f}% ROI). "
        f"Job demand index: {demand:.0f}/100."
    )

    return CareerSimResponse(
        predicted_starting_salary=round(starting_salary, 0),
        salary_at_5yr=round(sal_5yr, 0),
        salary_at_10yr=round(sal_10yr, 0),
        total_investment=round(total_investment, 0),
        break_even_years=break_even,
        ten_year_net=round(ten_yr_net, 0),
        roi_percent=roi_pct,
        demand_index=demand,
        career_grade=grade,
        projections=projections,
        top_skills_to_add=skills,
        summary=summary,
    )
