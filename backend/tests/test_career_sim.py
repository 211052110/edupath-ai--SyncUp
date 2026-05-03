"""
Tests: Career Simulator
"""

import pytest
from app.schemas.career_sim import CareerSimRequest
from app.services.career_sim_service import (
    simulate_career, _demand_index, _growth_rate, _top_skills, _career_grade
)


# ── Unit: helpers ─────────────────────────────────────────────────────────────

class TestDemandIndex:
    def test_usa_ml_engineer_high(self):
        assert _demand_index("USA", "ml engineer") >= 90

    def test_unknown_defaults_to_value(self):
        val = _demand_index("USA", "unknown_role_xyz")
        assert 0 <= val <= 100

    def test_germany_lower_than_usa_ml(self):
        assert _demand_index("Germany", "ml engineer") < _demand_index("USA", "ml engineer")


class TestGrowthRate:
    def test_ml_higher_than_analyst(self):
        assert _growth_rate("ml engineer") > _growth_rate("data analyst")

    def test_unknown_returns_default(self):
        rate = _growth_rate("unknownrole")
        assert rate == pytest.approx(0.065)

    def test_all_rates_positive(self):
        for role in ["data scientist", "ml engineer", "software engineer",
                     "ai researcher", "data analyst", "full stack"]:
            assert _growth_rate(role) > 0


class TestCareerGrade:
    def test_high_scores_get_a_plus(self):
        assert _career_grade(100, 100, 150) == "A+"

    def test_low_scores_get_c(self):
        assert _career_grade(0, 0, 0) == "C"

    def test_grade_is_valid(self):
        g = _career_grade(70, 80, 100)
        assert g in ("A+", "A", "B+", "B", "C")


class TestTopSkills:
    def test_returns_list(self):
        skills = _top_skills("USA", "AI")
        assert isinstance(skills, list)
        assert len(skills) > 0

    def test_unknown_returns_defaults(self):
        skills = _top_skills("Mars", "quantum poetry")
        assert len(skills) > 0


# ── Unit: simulate_career ─────────────────────────────────────────────────────

class TestSimulateCareer:
    def _req(self, **kw):
        defaults = dict(
            gpa=3.7, field_of_study="Computer Science", target_country="USA",
            work_experience_years=2, program_duration_years=2,
            annual_tuition_usd=45000, monthly_living_usd=1500,
            target_role="Data Scientist",
        )
        defaults.update(kw)
        return CareerSimRequest(**defaults)

    def test_returns_response(self):
        r = simulate_career(self._req())
        assert r is not None

    def test_starting_salary_positive(self):
        r = simulate_career(self._req())
        assert r.predicted_starting_salary > 0

    def test_salary_grows(self):
        r = simulate_career(self._req())
        assert r.salary_at_10yr > r.salary_at_5yr > r.predicted_starting_salary

    def test_10_year_projections(self):
        r = simulate_career(self._req())
        assert len(r.projections) == 10

    def test_projections_salary_increasing(self):
        r = simulate_career(self._req())
        salaries = [p.salary for p in r.projections]
        assert all(salaries[i] <= salaries[i+1] for i in range(len(salaries)-1))

    def test_break_even_positive(self):
        r = simulate_career(self._req())
        assert r.break_even_years > 0

    def test_demand_index_in_range(self):
        r = simulate_career(self._req())
        assert 0 <= r.demand_index <= 100

    def test_grade_valid(self):
        r = simulate_career(self._req())
        assert r.career_grade in ("A+", "A", "B+", "B", "C")

    def test_summary_not_empty(self):
        r = simulate_career(self._req())
        assert len(r.summary) > 20

    def test_top_skills_returned(self):
        r = simulate_career(self._req())
        assert len(r.top_skills_to_add) > 0

    def test_total_investment_correct(self):
        r = simulate_career(self._req(annual_tuition_usd=40000, monthly_living_usd=1000,
                                       program_duration_years=2))
        expected = (40000 + 1000 * 12) * 2
        assert r.total_investment == pytest.approx(expected)

    def test_germany_lower_investment(self):
        r_de = simulate_career(self._req(target_country="Germany", annual_tuition_usd=500))
        r_us = simulate_career(self._req(target_country="USA", annual_tuition_usd=45000))
        assert r_de.total_investment < r_us.total_investment


# ── API: endpoint ─────────────────────────────────────────────────────────────

class TestCareerSimAPI:
    def test_200_valid(self, client, career_sim_payload):
        r = client.post("/api/v1/career-sim/simulate", json=career_sim_payload)
        assert r.status_code == 200

    def test_response_schema(self, client, career_sim_payload):
        data = client.post("/api/v1/career-sim/simulate", json=career_sim_payload).json()
        assert "predicted_starting_salary" in data
        assert "projections" in data
        assert "career_grade" in data

    def test_invalid_gpa_rejected(self, client, career_sim_payload):
        career_sim_payload["gpa"] = 5.0
        r = client.post("/api/v1/career-sim/simulate", json=career_sim_payload)
        assert r.status_code == 422

    def test_negative_tuition_rejected(self, client, career_sim_payload):
        career_sim_payload["annual_tuition_usd"] = -1
        r = client.post("/api/v1/career-sim/simulate", json=career_sim_payload)
        assert r.status_code == 422
