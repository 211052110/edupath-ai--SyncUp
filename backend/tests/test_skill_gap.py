"""
Tests: Skill Gap Analyzer
"""

import pytest
from app.schemas.skill_gap import SkillGapRequest
from app.services.skill_gap_service import analyze_skill_gap, _extract_skills


# ── Unit: skill extraction ────────────────────────────────────────────────────

class TestExtractSkills:
    def test_python_detected(self):
        skills = _extract_skills("I use Python and pandas for data analysis.", None)
        assert "Python" in skills

    def test_ml_detected(self):
        skills = _extract_skills("Experience with machine learning and TensorFlow.", None)
        assert "ML / AI" in skills

    def test_cloud_detected(self):
        skills = _extract_skills("Deployed models on AWS using Docker and Kubernetes.", None)
        assert "Cloud" in skills

    def test_empty_resume(self):
        skills = _extract_skills("", None)
        assert isinstance(skills, set)

    def test_case_insensitive(self):
        skills = _extract_skills("PYTHON and PANDAS experience.", None)
        assert "Python" in skills

    def test_multiple_skills(self):
        skills = _extract_skills(
            "Python, pandas, sklearn, AWS, Docker, SQL, React, research publication.", None
        )
        assert len(skills) >= 4


# ── Unit: analyze_skill_gap ───────────────────────────────────────────────────

class TestAnalyzeSkillGap:
    def _req(self, **kw):
        defaults = dict(
            resume_text="Python developer with sklearn, pandas, SQL, AWS experience.",
            target_role="data scientist",
            target_country="USA",
        )
        defaults.update(kw)
        return SkillGapRequest(**defaults)

    def test_returns_response(self):
        r = analyze_skill_gap(self._req())
        assert r is not None

    def test_radar_data_not_empty(self):
        r = analyze_skill_gap(self._req())
        assert len(r.radar_data) > 0

    def test_overall_match_in_range(self):
        r = analyze_skill_gap(self._req())
        assert 0 <= r.overall_match <= 100

    def test_matched_skills_are_list(self):
        r = analyze_skill_gap(self._req())
        assert isinstance(r.matched_skills, list)

    def test_missing_skills_are_list(self):
        r = analyze_skill_gap(self._req())
        assert isinstance(r.missing_skills, list)

    def test_recommendation_not_empty(self):
        r = analyze_skill_gap(self._req())
        assert len(r.top_recommendation) > 5

    def test_strong_resume_higher_match(self):
        strong = ("Python, pandas, sklearn, TensorFlow, PyTorch, machine learning, deep learning, "
                  "NLP, SQL, AWS, Docker, data science, statistics, research publication, "
                  "data visualization, matplotlib, communication, teamwork.")
        weak   = "I like learning."
        r_strong = analyze_skill_gap(self._req(resume_text=strong))
        r_weak   = analyze_skill_gap(self._req(resume_text=weak))
        assert r_strong.overall_match >= r_weak.overall_match

    def test_radar_scores_in_range(self):
        r = analyze_skill_gap(self._req())
        for item in r.radar_data:
            assert 0 <= item.user_score <= 100
            assert 0 <= item.industry_score <= 100

    def test_unknown_role_handled(self):
        r = analyze_skill_gap(self._req(target_role="Underwater Basket Weaver"))
        assert r is not None
        assert 0 <= r.overall_match <= 100


# ── API: endpoint ─────────────────────────────────────────────────────────────

class TestSkillGapAPI:
    def test_200_valid(self, client, skill_gap_payload):
        r = client.post("/api/v1/skill-gap/analyze", json=skill_gap_payload)
        assert r.status_code == 200

    def test_response_schema(self, client, skill_gap_payload):
        data = client.post("/api/v1/skill-gap/analyze", json=skill_gap_payload).json()
        assert "radar_data" in data
        assert "overall_match" in data
        assert "missing_skills" in data

    def test_too_short_resume_rejected(self, client, skill_gap_payload):
        skill_gap_payload["resume_text"] = "hi"
        r = client.post("/api/v1/skill-gap/analyze", json=skill_gap_payload)
        assert r.status_code == 422

    def test_missing_role_rejected(self, client, skill_gap_payload):
        del skill_gap_payload["target_role"]
        r = client.post("/api/v1/skill-gap/analyze", json=skill_gap_payload)
        assert r.status_code == 422
