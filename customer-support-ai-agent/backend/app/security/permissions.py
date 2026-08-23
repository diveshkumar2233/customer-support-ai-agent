"""Simple rate limiter (sliding window, in-memory).

WHY: prevents a single client from hammering the LLM endpoint (cost blowup)
or brute-forcing tool actions. In-memory is fine for a single instance /
portfolio demo; production would back this with Redis so limits are shared
across horizontally-scaled instances.
"""
import time
from collections import defaultdict, deque

from fastapi import HTTPException, status

from app.config.settings import get_settings

settings = get_settings()
_requests: dict[str, deque] = defaultdict(deque)


def enforce_rate_limit(client_key: str) -> None:
    now = time.time()
    window = _requests[client_key]
    while window and now - window[0] > 60:
        window.popleft()
    if len(window) >= settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please slow down.",
        )
    window.append(now)
