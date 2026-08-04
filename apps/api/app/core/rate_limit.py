"""
Rate Limiting Architecture.

Uses a token-bucket algorithm with Redis as the backing store.
Falls back to an in-process limiter when Redis is unavailable,
so the app never breaks in development.

Usage:
    @router.get("/endpoint")
    async def endpoint(_: None = Depends(rate_limit(limit=60, window_seconds=60))):
        ...
"""

import time
from collections import defaultdict
from datetime import datetime, timezone

from fastapi import HTTPException, Request

try:
    import redis

    _redis = redis.Redis.from_url("redis://localhost:6379/0", decode_responses=True)
    _redis_available = _redis.ping()
except Exception:
    _redis_available = False


class _InMemoryBucket:
    """Fallback token bucket for local development."""

    def __init__(self):
        self.buckets: dict[str, list[float]] = defaultdict(list)

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.time()
        self.buckets[key] = [t for t in self.buckets[key] if now - t < window_seconds]
        if len(self.buckets[key]) >= limit:
            return False
        self.buckets[key].append(now)
        return True


_in_memory = _InMemoryBucket()


def _client_key(request: Request) -> str:
    """Extract a client identifier from the request."""
    forwarded = request.headers.get("x-forwarded-for", "")
    ip = forwarded.split(",")[0].strip() if forwarded else request.client.host if request.client else "unknown"
    user = request.headers.get("authorization", "")[:20]
    return f"{ip}:{user}"


def rate_limit(limit: int = 60, window_seconds: int = 60):
    """Dependency factory — apply a rate limit to an endpoint.

    Returns a FastAPI dependency that raises HTTP 429 when exceeded.
    """
    async def dependency(request: Request):
        key = _client_key(request)
        allowed = False

        if _redis_available:
            try:
                current = _redis.get(key)
                if current is None:
                    _redis.setex(key, window_seconds, 1)
                    allowed = True
                elif int(current) < limit:
                    _redis.incr(key)
                    allowed = True
            except Exception:
                allowed = _in_memory.allow(key, limit, window_seconds)
        else:
            allowed = _in_memory.allow(key, limit, window_seconds)

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {window_seconds}s.",
                headers={"Retry-After": str(window_seconds)},
            )
        return None

    return dependency