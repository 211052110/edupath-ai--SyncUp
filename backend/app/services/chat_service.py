"""
Visa Chat Service — Groq SDK (direct, no LangChain dependency)
Model: llama-3.3-70b-versatile via Groq API (free)
"""

import json
import logging
from groq import Groq

from app.schemas.chat import ChatRequest, ChatResponse, ChatMessage
from app.core.session_store import get_history, append_messages
from app.core.config import settings

logger = logging.getLogger("edupath.chat")

SYSTEM_PROMPT = """You are an expert visa interview coach for student visas (F-1, UK Student, Schengen, Australian).
Simulate a real visa officer OR coach the student based on intent.

Intent types:
- "answer": Evaluate like a visa officer. Score 0-100.
- "help": Give warm coaching guidance.
- "navigation": Briefly acknowledge, move on.

ALWAYS return valid JSON only — no markdown, no backticks.

For intent="answer":
{"message": "<officer feedback, 1-2 sentences>", "confidence_score": <0-100>, "strengths": ["<strength>"], "weaknesses": ["<weakness>"], "suggested_improvement": "<tip>", "tip": null, "topic_progress": <0-100>, "is_topic_complete": <true/false>}

Scoring: 85-100=specific amounts+documents, 60-84=mostly clear, 40-59=vague, 0-39=incomplete.

For intent="help":
{"message": "<coaching advice>", "tip": "<actionable tip>", "confidence_score": null, "strengths": null, "weaknesses": null, "suggested_improvement": null, "topic_progress": 0, "is_topic_complete": false}

For intent="navigation":
{"message": "<brief ack>", "tip": null, "confidence_score": null, "strengths": null, "weaknesses": null, "suggested_improvement": null, "topic_progress": 0, "is_topic_complete": false}"""


def _build_messages(history: list[ChatMessage], user_context: str) -> list[dict]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history[-20:]:
        role = "user" if msg.role == "user" else "assistant"
        messages.append({"role": role, "content": msg.content})
    messages.append({"role": "user", "content": user_context})
    return messages


def generate_chat_response(data: ChatRequest) -> ChatResponse:
    key = settings.GROQ_API_KEY.strip()
    if not key or key.startswith("gsk_your"):
        return ChatResponse(
            message="Groq API key not set. Open backend/.env, add your GROQ_API_KEY from console.groq.com (free), then restart the backend.",
            topic_progress=0,
            is_topic_complete=False,
        )

    server_history = get_history(data.session_id, data.topic_id)
    user_context = (
        f"Current Question: \"{data.current_question}\"\n"
        f"Intent: {data.intent}\n"
        f"Exchange count: {len(server_history)}\n"
        f"Student: \"{data.message}\""
    )
    messages = _build_messages(server_history, user_context)

    try:
        client = Groq(api_key=key)
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.4,
            max_tokens=600,
        )
        raw = resp.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)
        response_obj = ChatResponse(
            message=result.get("message", "Could you elaborate on that?"),
            tip=result.get("tip"),
            confidence_score=result.get("confidence_score"),
            strengths=result.get("strengths"),
            weaknesses=result.get("weaknesses"),
            suggested_improvement=result.get("suggested_improvement"),
            topic_progress=int(result.get("topic_progress", 0)),
            is_topic_complete=bool(result.get("is_topic_complete", False)),
        )
        append_messages(data.session_id, data.topic_id, [
            ChatMessage(role="user", content=data.message),
            ChatMessage(role="assistant", content=response_obj.message),
        ])
        return response_obj

    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse error: {e}")
        return ChatResponse(message="I had trouble formatting my response. Please try again.", topic_progress=0, is_topic_complete=False)
    except Exception as e:
        err = str(e).lower()
        if "401" in err or "invalid_api_key" in err or "authentication" in err:
            msg = "Invalid Groq API key. Check GROQ_API_KEY in backend/.env"
        elif "rate_limit" in err or "429" in err:
            msg = "Rate limit reached. Wait a moment and try again."
        else:
            logger.error(f"Chat error: {e}")
            msg = "Service temporarily unavailable. Please try again."
        return ChatResponse(message=msg, topic_progress=0, is_topic_complete=False)
