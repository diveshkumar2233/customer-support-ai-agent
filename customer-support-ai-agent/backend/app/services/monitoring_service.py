"""
Structured logging + cost estimation.

WHY structured (JSON) logs with a request_id: plain-text logs are hard to
query at scale. Emitting one JSON line per request with a request_id lets
you trace a single conversation turn across services in a log aggregator
(e.g. CloudWatch/Datadog) and correlate latency/cost/errors.
"""
import json
import logging
import uuid
from datetime import datetime

logger = logging.getLogger("support_agent")
logging.basicConfig(level=logging.INFO)

# Rough per-1K-token pricing for cost estimation (update to match your provider)
PRICE_PER_1K_INPUT = 0.003
PRICE_PER_1K_OUTPUT = 0.015


def new_request_id() -> str:
    return str(uuid.uuid4())


def estimate_cost(token_usage: dict) -> float:
    total_input = sum(v.get("input", 0) for v in token_usage.values())
    total_output = sum(v.get("output", 0) for v in token_usage.values())
    return round((total_input / 1000) * PRICE_PER_1K_INPUT + (total_output / 1000) * PRICE_PER_1K_OUTPUT, 6)


def log_turn(request_id: str, session_id: str, latency_ms: dict, token_usage: dict, error: str | None = None):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id,
        "session_id": session_id,
        "latency_ms": latency_ms,
        "total_latency_ms": sum(latency_ms.values()) if latency_ms else 0,
        "token_usage": token_usage,
        "estimated_cost_usd": estimate_cost(token_usage),
        "error": error,
    }
    logger.info(json.dumps(entry))
    return entry
