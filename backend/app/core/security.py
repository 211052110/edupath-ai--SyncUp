"""
Security: API Key auth + in-memory rate limiting (30 req/min per key).
For hackathon use — no DB required.
"""

import time
from collections import defaultdict
from fastapi import HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# In-memory store: { api_key: [timestamp, ...] }
_request_log: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT = 30   # requests
WINDOW     = 60   # seconds


def _is_rate_limited(api_key: str) -> bool:
    now = time.time()
    window_start = now - WINDOW
    # Keep only timestamps within current window
    _request_log[api_key] = [t for t in _request_log[api_key] if t > window_start]
    if len(_request_log[api_key]) >= RATE_LIMIT:
        return True
    _request_log[api_key].append(now)
    return False


def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    # Skip auth in development mode
    if settings.ENV == "development":
        return "dev"

    if not api_key or api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key. Pass X-API-Key header.",
        )

    if _is_rate_limited(api_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: {RATE_LIMIT} requests per {WINDOW}s.",
        )

    return api_key
