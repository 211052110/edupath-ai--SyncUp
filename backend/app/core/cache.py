"""
EduPath Cache Layer
-------------------
Uses Redis if REDIS_URL is configured (Upstash free tier works).
Falls back to an in-memory TTL dict — zero config needed locally.

Free Redis options:
  - Upstash:  https://upstash.com  (10k req/day free)
              Set REDIS_URL=rediss://:password@host:port in backend/.env
  - Local:    docker run -p 6379:6379 redis:alpine
              Set REDIS_URL=redis://localhost:6379

If REDIS_URL is empty → silent fallback to in-memory cache.
"""

import json
import hashlib
import logging
import time
from typing import Any, Optional
from app.core.config import settings

logger = logging.getLogger("edupath.cache")

# ── In-memory fallback ────────────────────────────────────────────────────────

class _MemoryCache:
    """Thread-safe TTL dict. No dependencies."""
    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[str]:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.time() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: str, ttl: int):
        self._store[key] = (value, time.time() + ttl)

    def delete(self, key: str):
        self._store.pop(key, None)

    def info(self) -> dict:
        now = time.time()
        live = sum(1 for _, exp in self._store.values() if exp > now)
        return {"backend": "memory", "live_keys": live}


# ── Redis backend ─────────────────────────────────────────────────────────────

class _RedisCache:
    def __init__(self, url: str):
        import redis
        self._client = redis.from_url(url, decode_responses=True,
                                      socket_connect_timeout=2,
                                      socket_timeout=2)

    def get(self, key: str) -> Optional[str]:
        try:
            return self._client.get(key)
        except Exception as e:
            logger.warning(f"Redis GET failed: {e}")
            return None

    def set(self, key: str, value: str, ttl: int):
        try:
            self._client.setex(key, ttl, value)
        except Exception as e:
            logger.warning(f"Redis SET failed: {e}")

    def delete(self, key: str):
        try:
            self._client.delete(key)
        except Exception as e:
            logger.warning(f"Redis DEL failed: {e}")

    def info(self) -> dict:
        try:
            info = self._client.info("server")
            return {"backend": "redis", "version": info.get("redis_version")}
        except Exception:
            return {"backend": "redis", "status": "unreachable"}


# ── Factory ───────────────────────────────────────────────────────────────────

def _make_backend():
    url = getattr(settings, "REDIS_URL", "").strip()
    if url:
        try:
            import redis  # noqa: F401
            backend = _RedisCache(url)
            # Ping to verify connection
            backend._client.ping()
            logger.info(f"Cache: Redis connected ({url[:30]}...)")
            return backend
        except Exception as e:
            logger.warning(f"Redis unavailable ({e}) — falling back to in-memory cache")
    else:
        logger.info("Cache: REDIS_URL not set — using in-memory cache (fine for dev/demo)")
    return _MemoryCache()


_backend = None

def _get_backend():
    global _backend
    if _backend is None:
        _backend = _make_backend()
    return _backend


# ── Public API ────────────────────────────────────────────────────────────────

# TTLs (seconds)
TTL_LOAN    = 3600   # 1 hour  — deterministic on same inputs
TTL_ROI     = 3600   # 1 hour
TTL_UNI_QA  = 86400  # 24 hours — RAG answers stable
TTL_SKILL   = 1800   # 30 min


def _cache_key(namespace: str, payload: Any) -> str:
    """Stable hash of namespace + JSON-serialised payload."""
    raw = json.dumps(payload, sort_keys=True, default=str)
    digest = hashlib.sha256(f"{namespace}:{raw}".encode()).hexdigest()[:16]
    return f"edupath:{namespace}:{digest}"


def cache_get(namespace: str, payload: Any) -> Optional[Any]:
    key = _cache_key(namespace, payload)
    raw = _get_backend().get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def cache_set(namespace: str, payload: Any, value: Any, ttl: int):
    key = _cache_key(namespace, payload)
    _get_backend().set(key, json.dumps(value, default=str), ttl)


def cache_info() -> dict:
    return _get_backend().info()
