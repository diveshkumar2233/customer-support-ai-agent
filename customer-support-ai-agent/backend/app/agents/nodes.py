"""
LangGraph node functions.

Each function takes the AgentState and returns a partial-state dict to merge
in. This is the LangGraph convention: nodes are pure(ish) functions over
state, which makes each one independently unit-testable (see
tests/test_agent.py) and easy to explain in an interview one node at a time.
"""
import time
import re
from typing import Any

from sqlalchemy.orm import Session

from app.agents.prompts import (
    SYSTEM_PROMPT,
    INTENT_CLASSIFICATION_PROMPT,
    RESPONSE_GENERATION_PROMPT,
    CONFIDENCE_SCORING_PROMPT,
)
from app.agents.state import AgentState
from app.config.settings import get_settings
from app.rag.retriever import Retriever
from app.security.guardrails import should_escalate, FALLBACK_MESSAGE, apply_output_guardrails
from app.security.prompt_injection import check_prompt_injection
from app.services import llm_client
from app.tools.registry import TOOL_REGISTRY

settings = get_settings()
_retriever = Retriever()

INTENTS_NEEDING_RETRIEVAL = {"refund", "shipping", "warranty", "general_faq", "cancellation"}
INTENT_TO_TOOL = {
    "order_status": "get_order_status",
    "cancellation": "cancel_order",
    "refund": "request_refund",
}


def _fallback_intent(query: str) -> str:
    """Route common support-policy questions when an LLM label is unavailable."""
    text = query.lower()
    if "policy" in text or "how long" in text or "what is" in text:
        return "general_faq"
    if any(term in text for term in ("return", "refund", "money back")):
        return "refund"
    if any(term in text for term in ("shipping", "delivery", "ship", "tracking")):
        return "shipping"
    if any(term in text for term in ("warranty", "guarantee")):
        return "warranty"
    if any(term in text for term in ("cancel", "cancellation")):
        return "cancellation"
    if any(term in text for term in ("order status", "where is my order")):
        return "order_status"
    return "other"


def _timed(fn_name: str, state: AgentState, start: float) -> dict:
    latency = state.get("latency_ms", {})
    latency[fn_name] = round((time.perf_counter() - start) * 1000, 2)
    return {"latency_ms": latency}


# ---------------------------------------------------------------------------
# 1. Input safety check
# ---------------------------------------------------------------------------
def check_input_safety(state: AgentState) -> dict:
    """Guardrail node: block/flag prompt-injection attempts before reasoning."""
    start = time.perf_counter()
    result = check_prompt_injection(state["query"])
    update: dict[str, Any] = {}
    if result.is_suspicious:
        update.update(
            {
                "escalate": False,
                "final_response": (
                    "I can't process that request as phrased. I'm here to help with "
                    "orders, refunds, shipping, and account questions — how can I assist?"
                ),
                "error": "prompt_injection_blocked",
            }
        )
    update.update(_timed("check_input_safety", state, start))
    return update


# ---------------------------------------------------------------------------
# 2. Intent classification (reason/decide)
# ---------------------------------------------------------------------------
def classify_intent(state: AgentState) -> dict:
    start = time.perf_counter()
    resp = llm_client.generate(
        system=SYSTEM_PROMPT,
        user=INTENT_CLASSIFICATION_PROMPT.format(query=state["query"]),
        max_tokens=20,
    )
    intent = resp.text.strip().lower()
    if intent not in {"order_status", "cancellation", "refund", "shipping", "warranty",
                       "general_faq", "complaint", "other"}:
        intent = _fallback_intent(state["query"])

    update = {
        "intent": intent,
        "needs_retrieval": intent in INTENTS_NEEDING_RETRIEVAL,
        "needs_tool": intent in INTENT_TO_TOOL,
        "planned_tool": INTENT_TO_TOOL.get(intent),
        "token_usage": {
            **state.get("token_usage", {}),
            "classify_intent": {"input": resp.input_tokens, "output": resp.output_tokens},
        },
    }
    update.update(_timed("classify_intent", state, start))
    return update


# ---------------------------------------------------------------------------
# 3. RAG retrieval
# ---------------------------------------------------------------------------
def retrieve_knowledge(state: AgentState) -> dict:
    start = time.perf_counter()
    hits = _retriever.retrieve(state["query"])
    chunks = [
        {"title": h.title, "text": h.text, "source": h.source_path, "score": h.score} for h in hits
    ]
    update = {"retrieved_chunks": chunks}
    update.update(_timed("retrieve_knowledge", state, start))
    return update


# ---------------------------------------------------------------------------
# 4. Tool execution (with validation + sensitive-action confirmation)
# ---------------------------------------------------------------------------
def execute_tool(state: AgentState, db: Session) -> dict:
    start = time.perf_counter()
    tool_name = state.get("planned_tool")
    if not tool_name or tool_name not in TOOL_REGISTRY:
        update = {"tool_result": None}
        update.update(_timed("execute_tool", state, start))
        return update

    meta = TOOL_REGISTRY[tool_name]
    fn = meta["fn"]

    # naive arg extraction placeholder — in the real graph this comes from the
    # LLM's structured tool_use block; simplified here for a deterministic demo
    args = state.get("planned_tool_args", {})

    try:
        if tool_name in ("get_order_status", "cancel_order"):
            result = fn(db, args.get("order_id", ""))
        elif tool_name == "request_refund":
            result = fn(db, args.get("order_id", ""), args.get("reason", "customer requested"))
        else:
            result = fn(db, **args)
        update = {"tool_result": result}
    except Exception as exc:  # noqa: BLE001
        update = {"tool_result": {"success": False, "error": str(exc)}, "error": "tool_execution_failed"}

    update.update(_timed("execute_tool", state, start))
    return update


# ---------------------------------------------------------------------------
# 5. Response generation (grounded in retrieval + tool results)
# ---------------------------------------------------------------------------
def generate_response(state: AgentState) -> dict:
    start = time.perf_counter()

    context = "\n\n".join(
        f"[{c['title']}] {c['text']}" for c in state.get("retrieved_chunks", [])
    ) or "No relevant documents retrieved."
    tool_result = state.get("tool_result") or "No tool was called."

    prompt = RESPONSE_GENERATION_PROMPT.format(
        query=state["query"], context=context, tool_result=tool_result
    )
    resp = llm_client.generate(system=SYSTEM_PROMPT, user=prompt, max_tokens=settings.LLM_MAX_TOKENS)
    draft = resp.text.strip()

    update = {
        "draft_response": draft,
        "sources": [{"title": c["title"], "source": c["source"]} for c in state.get("retrieved_chunks", [])],
        "token_usage": {
            **state.get("token_usage", {}),
            "generate_response": {"input": resp.input_tokens, "output": resp.output_tokens},
        },
    }
    update.update(_timed("generate_response", state, start))
    return update


# ---------------------------------------------------------------------------
# 6. Confidence / safety validation
# ---------------------------------------------------------------------------
def validate_and_score(state: AgentState) -> dict:
    start = time.perf_counter()
    context = "\n\n".join(c["text"] for c in state.get("retrieved_chunks", [])) or "N/A"

    resp = llm_client.generate(
        system="",
        user=CONFIDENCE_SCORING_PROMPT.format(
            query=state["query"], context=context, answer=state.get("draft_response", "")
        ),
        max_tokens=32,
    )
    try:
        match = re.search(r"(?:0(?:\.\d+)?|1(?:\.0+)?)", resp.text)
        confidence = float(match.group()) if match else 0.5
    except ValueError:
        confidence = 0.5
    confidence = max(0.0, min(1.0, confidence))

    guard = apply_output_guardrails(state.get("draft_response", ""))
    escalate = should_escalate(confidence)

    update = {
        "confidence": confidence,
        "final_response": guard.redacted_text if not escalate else FALLBACK_MESSAGE,
        "escalate": escalate,
        "escalation_reason": "low_confidence" if escalate else None,
    }
    update.update(_timed("validate_and_score", state, start))
    return update


# ---------------------------------------------------------------------------
# 7. Human handoff
# ---------------------------------------------------------------------------
def human_handoff(state: AgentState, db: Session) -> dict:
    start = time.perf_counter()
    from app.tools.ticket_tools import escalate_to_human

    reason = state.get("escalation_reason") or "agent_requested_handoff"
    ticket = escalate_to_human(db, reason=f"{reason}: {state['query']}")
    update = {
        "final_response": state.get("final_response") or FALLBACK_MESSAGE,
        "tool_result": ticket,
    }
    update.update(_timed("human_handoff", state, start))
    return update
