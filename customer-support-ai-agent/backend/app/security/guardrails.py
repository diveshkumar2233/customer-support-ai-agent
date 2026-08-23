"""
Output + policy guardrails applied to every agent turn.

WHY separate from prompt_injection.py: injection detection guards the
INPUT; guardrails here guard the OUTPUT and the DECISION to act — e.g.
blocking a tool call for a customer_id that doesn't match the authenticated
session, redacting anything that looks like a secret before it's returned,
and enforcing the confidence-based escalation policy. Treat this as the
last line of defense before a response reaches the user.
"""
import re
from dataclasses import dataclass, field

from app.config.settings import get_settings

settings = get_settings()

SECRET_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),           # API-key-shaped strings
    re.compile(r"(?i)password\s*[:=]\s*\S+"),
    re.compile(r"\b\d{13,19}\b"),                  # credit-card-like number runs
]


@dataclass
class GuardrailResult:
    allowed: bool
    reason: str = ""
    redacted_text: str = ""
    flags: list[str] = field(default_factory=list)


def redact_secrets(text: str) -> str:
    for pattern in SECRET_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text


def check_unauthorized_action(requested_customer_id: str, session_customer_id: str) -> GuardrailResult:
    """Block any tool call touching another customer's data (IDOR protection)."""
    if requested_customer_id and requested_customer_id != session_customer_id:
        return GuardrailResult(
            allowed=False,
            reason="Requested action targets a different customer than the authenticated session.",
            flags=["unauthorized_action"],
        )
    return GuardrailResult(allowed=True)


def apply_output_guardrails(text: str) -> GuardrailResult:
    flags = []
    redacted = redact_secrets(text)
    if redacted != text:
        flags.append("secret_redacted")
    return GuardrailResult(allowed=True, redacted_text=redacted, flags=flags)


def should_escalate(confidence: float) -> bool:
    return confidence < settings.CONFIDENCE_THRESHOLD


FALLBACK_MESSAGE = (
    "I'm not confident enough to answer this accurately. "
    "I'll connect you with a support specialist who can help further."
)
