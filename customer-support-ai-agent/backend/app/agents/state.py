"""
Agent state schema shared across every LangGraph node.

WHY a typed state object: LangGraph passes this dict between nodes as a
single source of truth for the whole turn. Typing it (TypedDict) makes the
data flow self-documenting and catches key typos at development time
instead of at runtime deep in a chain.
"""
from typing import Any, Optional, TypedDict


class AgentState(TypedDict, total=False):
    # input
    query: str
    session_id: str
    customer_id: Optional[str]
    conversation_history: list[dict]  # [{"role": "user"/"assistant", "content": str}]

    # reasoning
    intent: str                        # e.g. "order_status", "refund", "faq", "other"
    needs_retrieval: bool
    needs_tool: bool
    planned_tool: Optional[str]
    planned_tool_args: dict

    # retrieval
    retrieved_chunks: list[dict]

    # tool execution
    tool_result: Optional[dict]
    tool_blocked_reason: Optional[str]

    # response
    draft_response: str
    confidence: float
    final_response: str
    sources: list[dict]

    # control flow
    escalate: bool
    escalation_reason: Optional[str]
    error: Optional[str]

    # observability
    token_usage: dict
    latency_ms: dict  # per-node latency
