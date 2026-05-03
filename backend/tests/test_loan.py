"""
Tests: Loan Scoring — service logic + API endpoint
"""

import pytest
from app.schemas.loan import LoanScoreRequest
from app.services.loan_service import calculate_eligibility, _build_features, _country_score


# ── Unit: feature engineering ─────────────────────────────────────────────────

class TestBuildFeatures:
    def _req(self, **kw):
        defaults = dict(gpa=3.5, annual_budget=55000, target_country="USA",
                        work_experience_years=2, english_score=7.5)
        defaults.update(kw)
        return LoanScoreRequest(**defaults)

    def test_feature_shape(self):
        X = _build_features(self._req())
        assert X.shape == (1, 7)

    def test_gpa_normalised(self):
        X = _build_features(self._req(gpa=4.0))
        assert X[0, 0] == pytest.approx(100.0)

    def test_gpa_clipped_at_100(self):
        X = _build_features(self._req(gpa=4.0))
        assert X[0, 0] <= 100.0

    def test_english_normalised(self):
        X = _build_features(self._req(english_score=9.0))
        assert X[0, 3] == pytest.approx(100.0)

    def test_work_exp_zero(self):
        X = _build_features(self._req(work_experience_years=0))
        assert X[0, 2] == pytest.approx(0.0)

    def test_composite_acad_positive(self):
        X = _build_features(self._req(gpa=3.5, english_score=7.5))
        assert X[0, 6] > 0


class TestCountryScore:
    def test_usa(self):
        assert _country_score("USA") == 92

    def test_germany(self):
        assert _country_score("Germany") == 95

    def test_unknown(self):
        assert _country_score("Zimbabwe") == 62

    def test_case_insensitive(self):
        assert _country_score("canada") == _country_score("Canada")


# ── Unit: service output ──────────────────────────────────────────────────────

class TestCalculateEligibility:
    def _req(self, **kw):
        defaults = dict(gpa=3.5, annual_budget=55000, target_country="USA",
                        work_experience_years=2, english_score=7.5)
        defaults.update(kw)
        return LoanScoreRequest(**defaults)

    def test_score_in_range(self):
        r = calculate_eligibility(self._req())
        assert 10 <= r.overall_score <= 99

    def test_classification_not_empty(self):
        r = calculate_eligibility(self._req())
        assert r.classification in ("Excellent", "Good", "Average", "Poor")

    def test_risk_level_set(self):
        r = calculate_eligibility(self._req())
        assert r.risk_level in ("Low Risk", "Medium Risk", "High Risk")

    def test_explanation_mentions_score(self):
        r = calculate_eligibility(self._req())
        assert str(r.overall_score) in r.explanation

    def test_factors_all_present(self):
        r = calculate_eligibility(self._req())
        expected_keys = {"academic_record", "financial_stability",
                         "employment_prospects", "country_risk", "english_proficiency"}
        assert expected_keys == set(r.factors.keys())

    def test_factors_in_range(self):
        r = calculate_eligibility(self._req())
        for v in r.factors.values():
            assert 0 <= v <= 100

    def test_lenders_returned(self):
        r = calculate_eligibility(self._req())
        assert len(r.recommended_lenders) >= 1

    def test_suggestions_not_empty(self):
        r = calculate_eligibility(self._req())
        assert len(r.improvement_suggestions) >= 1

    def test_model_info_present(self):
        r = calculate_eligibility(self._req())
        assert r.model_info is not None
        assert "model" in r.model_info

    def test_low_budget_triggers_suggestion(self):
        r = calculate_eligibility(self._req(annual_budget=10000))
        texts = " ".join(r.improvement_suggestions).lower()
        assert "scholarship" in texts or "collateral" in texts

    def test_low_english_triggers_suggestion(self):
        r = calculate_eligibility(self._req(english_score=5.0))
        texts = " ".join(r.improvement_suggestions).lower()
        assert "ielts" in texts or "toefl" in texts


# ── API: endpoint ─────────────────────────────────────────────────────────────

class TestLoanAPI:
    def test_200_valid(self, client, loan_payload):
        r = client.post("/api/v1/loan/calculate-score", json=loan_payload)
        assert r.status_code == 200

    def test_response_schema(self, client, loan_payload):
        data = client.post("/api/v1/loan/calculate-score", json=loan_payload).json()
        assert "overall_score" in data
        assert "recommended_lenders" in data
        assert "factors" in data

    def test_invalid_gpa_rejected(self, client, loan_payload):
        loan_payload["gpa"] = 5.0  # > 4.0
        r = client.post("/api/v1/loan/calculate-score", json=loan_payload)
        assert r.status_code == 422

    def test_negative_budget_rejected(self, client, loan_payload):
        loan_payload["annual_budget"] = -1
        r = client.post("/api/v1/loan/calculate-score", json=loan_payload)
        assert r.status_code == 422

    def test_missing_field_rejected(self, client):
        r = client.post("/api/v1/loan/calculate-score", json={"gpa": 3.5})
        assert r.status_code == 422

    def test_boundary_gpa_zero(self, client, loan_payload):
        loan_payload["gpa"] = 0.0
        r = client.post("/api/v1/loan/calculate-score", json=loan_payload)
        assert r.status_code == 200

    def test_boundary_gpa_max(self, client, loan_payload):
        loan_payload["gpa"] = 4.0
        r = client.post("/api/v1/loan/calculate-score", json=loan_payload)
        assert r.status_code == 200
