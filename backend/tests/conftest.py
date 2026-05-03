"""
conftest.py — shared fixtures for EduPath test suite.

Mocks:
  - ML models (loan + ROI) so tests run without .pkl files
  - Groq API calls (no API key needed)
  - spaCy (no download needed)
  - Live data (no HTTP calls)
  - Cache (always miss → pure function testing)
"""

import numpy as np
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


# ── Fake ML models ────────────────────────────────────────────────────────────

class _FakeLoanModel:
    """Mimics sklearn GBM / XGBoost / LightGBM classifier interface."""
    def predict_proba(self, X):
        # Always return medium-risk profile
        return np.array([[0.1, 0.6, 0.3]])

class _FakeScaler:
    def transform(self, X):
        return X

class _FakeROIModel:
    def predict(self, X):
        return np.array([95000.0])

class _FakeSHAPExplainer:
    def shap_values(self, X):
        return [np.zeros((1, 7)), np.zeros((1, 7)), np.zeros((1, 7))]


@pytest.fixture(autouse=True)
def mock_models(monkeypatch):
    """Patch model loader globally — no .pkl files needed."""
    fake_loan  = _FakeLoanModel()
    fake_scaler = _FakeScaler()
    fake_roi   = _FakeROIModel()

    monkeypatch.setattr("app.core.model_loader.get_loan_model",
                        lambda: (fake_loan, fake_scaler))
    monkeypatch.setattr("app.core.model_loader.get_roi_model",
                        lambda: fake_roi)
    monkeypatch.setattr("app.core.model_loader.get_loan_meta",
                        lambda: {"best_model": "XGBoost", "cv_auc": 0.972,
                                 "xgb_auc": 0.972, "lgb_auc": 0.969})


@pytest.fixture(autouse=True)
def mock_shap(monkeypatch):
    monkeypatch.setattr("shap.TreeExplainer", lambda m: _FakeSHAPExplainer())


@pytest.fixture(autouse=True)
def mock_live_data(monkeypatch):
    monkeypatch.setattr("app.services.live_data.get_salary_multiplier", lambda c: 1.0)
    monkeypatch.setattr("app.services.live_data.get_exchange_rate", lambda f, t: 83.5)


@pytest.fixture(autouse=True)
def mock_cache(monkeypatch):
    """Cache always misses so we test actual service logic."""
    monkeypatch.setattr("app.core.cache.cache_get", lambda ns, p: None)
    monkeypatch.setattr("app.core.cache.cache_set", lambda ns, p, v, ttl: None)
    monkeypatch.setattr("app.core.cache.cache_info", lambda: {"backend": "memory", "live_keys": 0})


@pytest.fixture(autouse=True)
def mock_spacy(monkeypatch):
    """Stub spaCy so skill gap tests run without model download."""
    fake_doc_tokens = []
    fake_doc = MagicMock()
    fake_doc.__iter__ = MagicMock(return_value=iter(fake_doc_tokens))
    fake_doc.ents = []
    fake_doc.noun_chunks = []
    fake_nlp = MagicMock(return_value=fake_doc)

    monkeypatch.setattr("app.services.skill_gap_service._get_nlp", lambda: fake_nlp)


@pytest.fixture(autouse=True)
def mock_groq(monkeypatch):
    """Stub Groq so chat/RAG tests don't need API key."""
    fake_msg     = MagicMock()
    fake_msg.content = '{"message":"Good answer.","confidence_score":82,"strengths":["clarity"],"weaknesses":["vague on funds"],"suggested_improvement":"Mention exact bank balance.","tip":null,"topic_progress":60,"is_topic_complete":false}'
    fake_choice  = MagicMock(); fake_choice.message = fake_msg
    fake_resp    = MagicMock(); fake_resp.choices = [fake_choice]

    fake_client  = MagicMock()
    fake_client.chat.completions.create.return_value = fake_resp

    monkeypatch.setattr("groq.Groq", lambda api_key=None: fake_client)

    # LangChain ChatGroq
    fake_lc_msg  = MagicMock()
    fake_lc_msg.content = fake_msg.content
    fake_llm     = MagicMock()
    fake_llm.invoke.return_value = fake_lc_msg
    monkeypatch.setattr("langchain_groq.ChatGroq", lambda **kw: fake_llm)


@pytest.fixture(autouse=True)
def mock_faiss(monkeypatch):
    """Stub FAISS vector store so RAG tests run without HuggingFace download."""
    from langchain.schema import Document
    fake_results = [
        (Document(page_content="MIT CS MS tuition ~$60,000/year. Cambridge MA."), 0.4),
        (Document(page_content="USA F-1 student visa requires I-20 form."), 0.5),
    ]
    fake_vs = MagicMock()
    fake_vs.similarity_search_with_score.return_value = fake_results
    monkeypatch.setattr("app.services.rag_service._get_vectorstore", lambda: fake_vs)


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


# ── Reusable payloads ─────────────────────────────────────────────────────────

@pytest.fixture
def loan_payload():
    return {
        "gpa": 3.5,
        "annual_budget": 55000,
        "target_country": "USA",
        "work_experience_years": 2,
        "english_score": 7.5,
    }

@pytest.fixture
def roi_payload():
    return {
        "duration_years": 2,
        "annual_tuition": 45000,
        "monthly_living_costs": 1500,
        "target_country": "USA",
        "field_of_study": "Computer Science",
        "expected_salary": 0,
    }

@pytest.fixture
def skill_gap_payload():
    return {
        "resume_text": "Python developer with 3 years experience in machine learning, sklearn, pandas, SQL, AWS.",
        "target_role": "data scientist",
        "target_country": "USA",
    }

@pytest.fixture
def career_sim_payload():
    return {
        "gpa": 3.7,
        "field_of_study": "Computer Science",
        "target_country": "USA",
        "work_experience_years": 2,
        "program_duration_years": 2,
        "annual_tuition_usd": 45000,
        "monthly_living_usd": 1500,
        "target_role": "Data Scientist",
    }
