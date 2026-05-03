"""
Tests: ROI Calculator — service logic + API endpoint
"""

import pytest
from app.schemas.roi import ROIRequest
from app.services.roi_service import calculate_roi, _emi, _encode_country, _encode_field


# ── Unit: helpers ─────────────────────────────────────────────────────────────

class TestHelpers:
    def test_emi_positive(self):
        assert _emi(50000, 0.115, 7) > 0

    def test_emi_zero_rate(self):
        # Should not raise; falls back to principal/n
        result = _emi(12000, 0.0, 1)
        assert result == 1000

    def test_encode_country_usa(self):
        assert _encode_country("United States") == 0

    def test_encode_country_germany(self):
        assert _encode_country("Germany") == 1

    def test_encode_country_unknown(self):
        assert _encode_country("Zimbabwe") == 0  # defaults to USA

    def test_encode_field_cs(self):
        assert _encode_field("Computer Science") == 0

    def test_encode_field_ai(self):
        assert _encode_field("Artificial Intelligence") == 2

    def test_encode_field_unknown(self):
        assert _encode_field("Medieval History") == 0  # default


# ── Unit: service output ──────────────────────────────────────────────────────

class TestCalculateROI:
    def _req(self, **kw):
        defaults = dict(duration_years=2, annual_tuition=45000,
                        monthly_living_costs=1500, target_country="USA",
                        field_of_study="Computer Science", expected_salary=0)
        defaults.update(kw)
        return ROIRequest(**defaults)

    def test_returns_response(self):
        r = calculate_roi(self._req())
        assert r is not None

    def test_total_investment_correct(self):
        r = calculate_roi(self._req(annual_tuition=40000, monthly_living_costs=1000,
                                    duration_years=2, expected_salary=100000))
        expected = (40000 + 1000 * 12) * 2
        assert r.metrics.total_investment == expected

    def test_ten_year_earnings_positive(self):
        r = calculate_roi(self._req())
        assert r.metrics.ten_year_earnings > 0

    def test_projection_has_10_points(self):
        r = calculate_roi(self._req())
        assert len(r.projection_data) == 10

    def test_projection_years_labelled(self):
        r = calculate_roi(self._req())
        assert r.projection_data[0].year == "Y1"
        assert r.projection_data[9].year == "Y10"

    def test_break_even_after_study(self):
        r = calculate_roi(self._req(duration_years=2))
        assert r.metrics.break_even_year >= 2

    def test_emi_positive(self):
        r = calculate_roi(self._req())
        assert r.metrics.monthly_emi > 0

    def test_insight_text_not_empty(self):
        r = calculate_roi(self._req())
        assert len(r.insights.insight_text) > 10

    def test_comparison_includes_roi(self):
        r = calculate_roi(self._req())
        assert "%" in r.insights.comparison

    def test_expected_salary_overrides_model(self):
        r1 = calculate_roi(self._req(expected_salary=0))
        r2 = calculate_roi(self._req(expected_salary=200000))
        assert r2.metrics.ten_year_earnings > r1.metrics.ten_year_earnings

    def test_germany_roi_better_than_uk(self):
        r_de = calculate_roi(self._req(target_country="Germany", annual_tuition=500,
                                       expected_salary=72000))
        r_uk = calculate_roi(self._req(target_country="UK", annual_tuition=35000,
                                       expected_salary=65000))
        assert r_de.metrics.ten_year_roi_percentage > r_uk.metrics.ten_year_roi_percentage


# ── API: endpoint ─────────────────────────────────────────────────────────────

class TestROIAPI:
    def test_200_valid(self, client, roi_payload):
        r = client.post("/api/v1/roi/calculate", json=roi_payload)
        assert r.status_code == 200

    def test_response_has_metrics(self, client, roi_payload):
        data = client.post("/api/v1/roi/calculate", json=roi_payload).json()
        assert "metrics" in data
        assert "projection_data" in data
        assert "insights" in data

    def test_duration_zero_rejected(self, client, roi_payload):
        roi_payload["duration_years"] = 0
        r = client.post("/api/v1/roi/calculate", json=roi_payload)
        assert r.status_code == 422

    def test_negative_tuition_rejected(self, client, roi_payload):
        roi_payload["annual_tuition"] = -1000
        r = client.post("/api/v1/roi/calculate", json=roi_payload)
        assert r.status_code == 422

    def test_missing_country_rejected(self, client, roi_payload):
        del roi_payload["target_country"]
        r = client.post("/api/v1/roi/calculate", json=roi_payload)
        assert r.status_code == 422
