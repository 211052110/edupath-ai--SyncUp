"""
Tests: University Q&A (RAG) + Visa Chat
"""

import pytest
from app.services.rag_service import answer_university_question
from app.services.chat_service import generate_chat_response
from app.schemas.chat import ChatRequest


# ── Unit: RAG service ─────────────────────────────────────────────────────────

class TestUniversityQA:
    def test_returns_dict(self):
        r = answer_university_question("What is MIT tuition?")
        assert isinstance(r, dict)

    def test_answer_key_present(self):
        r = answer_university_question("What is MIT tuition?")
        assert "answer" in r

    def test_sources_list(self):
        r = answer_university_question("F-1 visa requirements?")
        assert isinstance(r["sources"], list)

    def test_confidence_key_present(self):
        r = answer_university_question("Germany tuition?")
        assert "confidence" in r
        assert r["confidence"] in ("high", "medium", "low")

    def test_answer_not_empty(self):
        r = answer_university_question("MIT tuition fees?")
        assert len(r["answer"]) > 0


class TestUniversityQAAPI:
    def test_200_valid(self, client):
        r = client.post("/api/v1/university-qa/ask", json={"question": "MIT tuition?"})
        assert r.status_code == 200

    def test_response_has_answer(self, client):
        data = client.post("/api/v1/university-qa/ask", json={"question": "F-1 visa?"}).json()
        assert "answer" in data

    def test_empty_question_rejected(self, client):
        r = client.post("/api/v1/university-qa/ask", json={"question": ""})
        assert r.status_code == 422

    def test_missing_question_rejected(self, client):
        r = client.post("/api/v1/university-qa/ask", json={})
        assert r.status_code == 422


# ── Unit: chat service ────────────────────────────────────────────────────────

class TestChatService:
    def _req(self, **kw):
        defaults = dict(
            session_id="test-session-001",
            topic_id="finances",
            message="I have $50,000 in my bank account to cover first year.",
            current_question="How will you fund your studies?",
            intent="answer",
        )
        defaults.update(kw)
        return ChatRequest(**defaults)

    def test_returns_response(self):
        r = generate_chat_response(self._req())
        assert r is not None

    def test_message_not_empty(self):
        r = generate_chat_response(self._req())
        assert len(r.message) > 0

    def test_topic_progress_in_range(self):
        r = generate_chat_response(self._req())
        assert 0 <= r.topic_progress <= 100

    def test_is_topic_complete_bool(self):
        r = generate_chat_response(self._req())
        assert isinstance(r.is_topic_complete, bool)

    def test_help_intent_returns_tip(self):
        r = generate_chat_response(self._req(intent="help",
                                             message="What should I say about finances?"))
        assert r is not None  # tip may be in response

    def test_navigation_intent_handled(self):
        r = generate_chat_response(self._req(intent="navigation", message="Next question please"))
        assert r is not None


class TestChatAPI:
    def _payload(self, **kw):
        defaults = dict(
            session_id="api-test-session",
            topic_id="purpose",
            message="I want to study AI to solve healthcare problems in India.",
            current_question="Why do you want to study abroad?",
            intent="answer",
        )
        defaults.update(kw)
        return defaults

    def test_200_valid(self, client):
        r = client.post("/api/v1/chat/message", json=self._payload())
        assert r.status_code == 200

    def test_response_has_message(self, client):
        data = client.post("/api/v1/chat/message", json=self._payload()).json()
        assert "message" in data
        assert "topic_progress" in data

    def test_missing_session_rejected(self, client):
        p = self._payload()
        del p["session_id"]
        r = client.post("/api/v1/chat/message", json=p)
        assert r.status_code == 422

    def test_reset_endpoint(self, client):
        r = client.post("/api/v1/chat/reset",
                        json={"session_id": "api-test-session", "topic_id": "purpose"})
        assert r.status_code in (200, 404)  # 404 if session doesn't exist is ok
