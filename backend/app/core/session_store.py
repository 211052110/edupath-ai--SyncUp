"""
In-memory session store for chat history.
For hackathon: dict-based, auto-expires after 2 hours.
Production upgrade: replace with Redis.
"""

import time
from typing import Optional
from app.schemas.chat import ChatMessage

SESSION_TTL = 60 * 60 * 2  # 2 hours

# { session_id: { "history": [...], "last_active": float, "topic_id": str } }
_store: dict[str, dict] = {}


def _prune():
    """Remove expired sessions."""
    now = time.time()
    expired = [sid for sid, data in _store.items() if now - data["last_active"] > SESSION_TTL]
    for sid in expired:
        del _store[sid]


def get_history(session_id: str, topic_id: str) -> list[ChatMessage]:
    _prune()
    session = _store.get(session_id)
    # Reset history if topic changed
    if not session or session.get("topic_id") != topic_id:
        return []
    return session["history"]


def append_messages(session_id: str, topic_id: str, messages: list[ChatMessage]):
    _prune()
    if session_id not in _store or _store[session_id].get("topic_id") != topic_id:
        _store[session_id] = {"history": [], "topic_id": topic_id, "last_active": time.time()}
    _store[session_id]["history"].extend(messages)
    _store[session_id]["last_active"] = time.time()
    # Cap at last 30 messages to avoid unbounded growth
    _store[session_id]["history"] = _store[session_id]["history"][-30:]


def clear_session(session_id: str):
    _store.pop(session_id, None)


def session_exists(session_id: str) -> bool:
    return session_id in _store
