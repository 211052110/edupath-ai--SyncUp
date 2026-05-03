"""
ROI Calculation Service
- XGBoost salary regressor (joblib-persisted) replaces hardcoded benchmarks
- Monte Carlo simulation (1000 runs) for earnings uncertainty
- Reducing-balance EMI formula
- World Bank GDP multiplier via live_data
"""

import numpy as np
from app.schemas.roi import ROIRequest, ROIResponse, ROIMetrics, ProjectionData, ROIInsights
from app.services.live_data import get_salary_multiplier, get_exchange_rate
from app.core.model_loader import get_roi_model

# Country + field encodings (must match train_models.py)
COUNTRY_ENC = {"usa": 0, "germany": 1, "uk": 2, "united kingdom": 2,
               "canada": 3, "australia": 4}
FIELD_ENC   = {"computer science": 0, "data science": 1,
               "ai": 2, "machine learning": 2, "artificial intelligence": 2,
               "business": 3, "administration": 3,
               "finance": 4}

# Fallback benchmarks if model unavailable
SALARY_FALLBACK = {
    ("usa", "computer science"): 115000, ("usa", "ai"): 130000,
    ("germany", "computer science"): 72000, ("uk", "computer science"): 65000,
    ("canada", "computer science"): 90000, ("australia", "computer science"): 88000,
}

COUNTRY_AVG_ROI = {"USA": 580, "Germany": 820, "Canada": 510, "Australia": 490, "UK": 470}

ANNUAL_GROWTH_RATE  = 0.035
LOAN_INTEREST_RATE  = 0.1150
LOAN_DURATION_YEARS = 7
MONTE_CARLO_RUNS    = 1000


def _encode_country(country: str) -> int:
    cl = country.lower()
    for k, v in COUNTRY_ENC.items():
        if k in cl:
            return v
    return 0  # default USA


def _encode_field(field: str) -> int:
    fl = field.lower()
    for k, v in FIELD_ENC.items():
        if k in fl:
            return v
    return 0  # default CS


def _predict_salary(data: ROIRequest) -> float:
    """Use XGBoost model to predict starting salary."""
    try:
        model = get_roi_model()
        gpa_n    = min(100.0, (3.5 / 4.0) * 100)   # neutral GPA (user doesn't input this)
        tui_n    = min(100.0, (data.annual_tuition / 80000) * 100)
        liv_n    = min(100.0, (data.monthly_living_costs / 3000) * 100)
        country  = float(_encode_country(data.target_country))
        field    = float(_encode_field(data.field_of_study))
        work_n   = 2.0 * 14   # assume 2yr work exp (conservative)
        X = np.array([[gpa_n, data.duration_years, tui_n, liv_n, country, field, work_n]])
        return float(model.predict(X)[0])
    except Exception:
        # Fallback to hardcoded median
        cl = data.target_country.lower()[:3]
        fl = data.field_of_study.lower()
        for (c, f), sal in SALARY_FALLBACK.items():
            if c in cl and f in fl:
                return float(sal)
        return 75000.0


def _emi(principal: float, annual_rate: float, years: int) -> int:
    r = annual_rate / 12
    n = years * 12
    if r == 0:
        return int(principal / n)
    return int(round(principal * r * (1 + r) ** n / ((1 + r) ** n - 1)))


def calculate_roi(data: ROIRequest) -> ROIResponse:
    rng = np.random.default_rng(42)

    total_cost = int((data.annual_tuition + data.monthly_living_costs * 12) * data.duration_years)

    # Salary: user input if provided, else XGBoost prediction × live GDP multiplier
    model_salary    = _predict_salary(data)
    live_multiplier = get_salary_multiplier(data.target_country)
    adjusted_salary = model_salary * live_multiplier
    base_salary     = data.expected_salary if data.expected_salary > 0 else adjusted_salary

    std_dev = base_salary * 0.12  # 12% std dev for MC

    mc_total_earnings = []
    for _ in range(MONTE_CARLO_RUNS):
        salary = max(rng.normal(base_salary, std_dev), base_salary * 0.5)
        total  = sum(salary * (1 + ANNUAL_GROWTH_RATE) ** yr for yr in range(10))
        mc_total_earnings.append(total)

    mc_arr           = np.array(mc_total_earnings)
    ten_year_earnings = int(np.median(mc_arr))
    earnings_p25     = int(np.percentile(mc_arr, 25))
    earnings_p75     = int(np.percentile(mc_arr, 75))
    roi_percentage   = int(((ten_year_earnings - total_cost) / max(total_cost, 1)) * 100)

    cumulative = 0.0
    break_even_year = None
    for yr in range(1, 21):
        cumulative += base_salary * (1 + ANNUAL_GROWTH_RATE) ** (yr - 1)
        if cumulative >= total_cost:
            break_even_year = round(data.duration_years + yr, 1)
            break
    if break_even_year is None:
        break_even_year = float(data.duration_years + 20)

    monthly_emi = _emi(total_cost * 1.0, LOAN_INTEREST_RATE, LOAN_DURATION_YEARS)

    projection = []
    current_cost = 0
    current_earnings = 0
    annual_expense = data.annual_tuition + data.monthly_living_costs * 12
    for yr in range(1, 11):
        if yr <= data.duration_years:
            current_cost += annual_expense
        else:
            post_yr = yr - data.duration_years
            current_earnings += int(base_salary * (1 + ANNUAL_GROWTH_RATE) ** (post_yr - 1))
        projection.append(ProjectionData(year=f"Y{yr}", cost=current_cost, earnings=current_earnings))

    metrics = ROIMetrics(
        total_investment=total_cost,
        ten_year_earnings=ten_year_earnings,
        ten_year_roi_percentage=roi_percentage,
        break_even_year=break_even_year,
        monthly_emi=monthly_emi,
        loan_duration_years=LOAN_DURATION_YEARS,
    )

    post_study_break_even = break_even_year - data.duration_years
    if post_study_break_even <= 3:
        insight_text   = (f"Break-even in {break_even_year} yrs is excellent for {data.field_of_study}. "
                          f"MC P25–P75 earnings: ${earnings_p25:,}–${earnings_p75:,}.")
        recommendation = "Strong case. Prioritise Poonawalla Fincorp or HDFC Credila for competitive rates."
    elif post_study_break_even <= 6:
        insight_text   = (f"Break-even in {break_even_year} yrs is average for {data.field_of_study}. "
                          f"Earnings range: ${earnings_p25:,}–${earnings_p75:,} over 10 years.")
        recommendation = "Viable. Negotiate longer tenure (7–10 yrs) to reduce monthly EMI pressure."
    else:
        insight_text   = (f"Break-even in {break_even_year} yrs is slower than typical. "
                          f"Conservative estimate: ${earnings_p25:,} over 10 years.")
        recommendation = "High risk. Target scholarships or lower-cost universities to improve ROI."

    country_avg = COUNTRY_AVG_ROI.get(
        next((k for k in COUNTRY_AVG_ROI if k.lower() in data.target_country.lower()), ""), 460
    )
    diff = roi_percentage - country_avg
    usd_to_inr      = get_exchange_rate("USD", "INR")
    monthly_emi_inr = int(metrics.monthly_emi * usd_to_inr)
    comparison = (
        f"Projected ROI ({roi_percentage}%) is {abs(diff)}% "
        f"{'above' if diff >= 0 else 'below'} {data.target_country} avg ({country_avg}%). "
        f"EMI in INR: ₹{monthly_emi_inr:,}/mo at ₹{usd_to_inr:.1f}/USD."
    )

    xgb_note = f" (Salary predicted by XGBoost: ${int(model_salary):,}/yr base)" if data.expected_salary == 0 else ""
    insights = ROIInsights(
        insight_text=insight_text + xgb_note,
        recommendation=recommendation,
        comparison=comparison,
    )

    return ROIResponse(metrics=metrics, insights=insights, projection_data=projection)
