"""
Loan Scoring Service — SMOTE + Optuna-tuned LightGBM/XGBoost + SHAP
Model loaded from disk (models/loan_gbm.pkl).
Falls back to training on first boot if .pkl missing.
"""

import numpy as np
import shap
from app.schemas.loan import LoanScoreRequest, LoanScoreResponse, LenderRecommendation
from app.services.lender_config import get_lenders_for
from app.core.model_loader import get_loan_model, get_loan_meta

PREMIUM_COUNTRIES = {
    "USA": 92, "Germany": 95, "Canada": 90, "Australia": 88,
    "UK": 87, "Netherlands": 85, "Singapore": 84, "New Zealand": 82,
    "Ireland": 80, "Sweden": 80,
}


def _country_score(target_country: str) -> int:
    for country, score in PREMIUM_COUNTRIES.items():
        if country.lower() in target_country.lower():
            return score
    return 62


def _build_features(data: LoanScoreRequest) -> np.ndarray:
    gpa_norm       = min(100.0, (data.gpa / 4.0) * 100.0)
    budget_norm    = min(100.0, (data.annual_budget / 80000.0) * 100.0)
    work_exp_norm  = min(100.0, data.work_experience_years * 14.0)
    english_norm   = min(100.0, (data.english_score / 9.0) * 100.0)
    country_risk   = float(_country_score(data.target_country))
    debt_to_income = data.annual_budget / max(1, data.annual_budget + 30000) * 100
    composite_acad = (gpa_norm * english_norm) / 100.0
    return np.array([[gpa_norm, budget_norm, work_exp_norm, english_norm,
                      country_risk, debt_to_income, composite_acad]])


def calculate_eligibility(data: LoanScoreRequest) -> LoanScoreResponse:
    model, scaler = get_loan_model()
    meta = get_loan_meta()

    X_raw    = _build_features(data)
    X_scaled = scaler.transform(X_raw)

    proba         = model.predict_proba(X_scaled)[0]
    raw_score     = int(round(proba[0] * 20 + proba[1] * 60 + proba[2] * 95))
    overall_score = max(10, min(99, raw_score))

    if overall_score >= 76:
        risk_level     = "Low Risk"
        classification = "Excellent" if overall_score >= 86 else "Good"
    elif overall_score >= 51:
        risk_level     = "Medium Risk"
        classification = "Average"
    else:
        risk_level     = "High Risk"
        classification = "Poor"

    # SHAP explanation — TreeExplainer works for XGBoost, LightGBM, GBM
    try:
        explainer  = shap.TreeExplainer(model)
        shap_vals  = explainer.shap_values(X_scaled)
        sv = shap_vals[2][0] if isinstance(shap_vals, list) else shap_vals[0]
    except Exception:
        sv = np.zeros(7)

    feature_vals = X_raw[0]
    factors = {
        "academic_record":      int(np.clip(feature_vals[0], 0, 100)),
        "financial_stability":  int(np.clip(feature_vals[1], 0, 100)),
        "employment_prospects": int(np.clip(feature_vals[2], 0, 100)),
        "country_risk":         int(np.clip(feature_vals[4], 0, 100)),
        "english_proficiency":  int(np.clip(feature_vals[3], 0, 100)),
    }

    shap_map = {
        "academic_record": sv[0], "financial_stability": sv[1],
        "employment_prospects": sv[2], "english_proficiency": sv[3],
        "country_risk": sv[4],
    }
    top_driver  = max(shap_map, key=lambda k: shap_map[k])
    top_detract = min(shap_map, key=lambda k: shap_map[k])

    driver_labels = {
        "academic_record":      f"strong academic record (GPA {data.gpa:.1f})",
        "financial_stability":  f"solid financial backing (${data.annual_budget:,}/yr)",
        "employment_prospects": f"{data.work_experience_years} year(s) of work experience",
        "english_proficiency":  f"English proficiency score of {data.english_score}",
        "country_risk":         f"high-demand destination ({data.target_country})",
    }
    detract_labels = {
        "academic_record":      f"GPA of {data.gpa:.1f} reduces lender confidence",
        "financial_stability":  f"annual budget of ${data.annual_budget:,} is below preferred threshold",
        "employment_prospects": "limited work experience increases risk perception",
        "english_proficiency":  f"English score of {data.english_score} is below the preferred 7.0+",
        "country_risk":         f"{data.target_country} carries higher post-study employment uncertainty",
    }

    explanation = (
        f"Your loan score is {overall_score} ({classification}), driven primarily by your "
        f"{driver_labels.get(top_driver, top_driver)}. "
        f"The main factor holding it back: {detract_labels.get(top_detract, top_detract)}. "
        f"Lenders classify this as a {risk_level.lower()} profile."
    )

    suggestions = []
    if factors["financial_stability"] < 65:
        suggestions.append("Add a creditworthy co-applicant or increase collateral to strengthen your file.")
    if factors["english_proficiency"] < 75:
        suggestions.append("Retake IELTS/TOEFL — a score of 7.0+ significantly improves lender confidence.")
    if factors["academic_record"] < 65:
        suggestions.append("Offset a lower GPA with strong SOP, LORs, or higher standardised test scores.")
    if factors["employment_prospects"] < 50:
        suggestions.append("1–2 years of relevant internship/work experience can raise your score by 8–12 points.")
    if data.annual_budget < 25000:
        suggestions.append("Explore university scholarships or assistantships to reduce the loan principal.")
    if not suggestions:
        suggestions.append("Maintain current standings. Applying with a co-signer may unlock lower interest rates.")

    raw_lenders = get_lenders_for(overall_score, data.target_country)
    recommended_lenders = [
        LenderRecommendation(
            name=l["name"], interest_rate=l["interest_rate"],
            max_amount=l["max_amount"], processing_time=l["processing_time"],
        ) for l in raw_lenders
    ]

    model_info = None
    if meta:
        model_info = {
            "model":   meta.get("best_model", "unknown"),
            "cv_auc":  round(meta["cv_auc"], 4) if meta.get("cv_auc") else None,
            "xgb_auc": round(meta["xgb_auc"], 4) if meta.get("xgb_auc") else None,
            "lgb_auc": round(meta["lgb_auc"], 4) if meta.get("lgb_auc") else None,
        }

    return LoanScoreResponse(
        overall_score=overall_score, classification=classification,
        explanation=explanation, risk_level=risk_level,
        improvement_suggestions=suggestions, factors=factors,
        recommended_lenders=recommended_lenders,
        model_info=model_info,
    )
