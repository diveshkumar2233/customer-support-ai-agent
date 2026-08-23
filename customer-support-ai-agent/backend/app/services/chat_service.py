"""
Orchestration layer between the API route and the agent graph.

WHY a service layer: keeps the FastAPI route thin (HTTP concerns only) and
the agent graph focused on reasoning — this is what makes each layer
independently testable and lets the same chat logic be reused by, say, a
Slack integration later without duplicating HTTP-handling code.
"""
import uuid

from sqlalchemy.orm import Session

from app.agents.graph import run_agent
from app.models.conversation import Conversation
from app.services.citation_service import format_citations
from app.services.memory_service import save_message
from app.services.monitoring_service import new_request_id, log_turn


def get_or_create_conversation(db: Session, session_id: str, customer_id: str | None) -> Conversation:
    convo = db.query(Conversation).filter(Conversation.session_id == session_id).first()
    if convo:
        return convo
    convo = Conversation(session_id=session_id, user_id=customer_id)
    db.add(convo)
    db.commit()
    db.refresh(convo)
    return convo


def handle_chat_turn(db: Session, session_id: str, customer_id: str | None, query: str) -> dict:
    request_id = new_request_id()
    convo = get_or_create_conversation(db, session_id, customer_id)

    save_message(db, str(convo.id), role="user", content=query)

    state = run_agent(query=query, session_id=session_id, customer_id=customer_id, db=db)

    final_response = state.get("final_response") or state.get("draft_response") or (
        "Something went wrong generating a response."
    )
    citations = format_citations(state.get("sources", []))

    save_message(
        db,
        str(convo.id),
        role="assistant",
        content=final_response,
        sources=citations,
        tool_calls=[state.get("planned_tool")] if state.get("planned_tool") else [],
        confidence=state.get("confidence"),
        latency_ms=sum(state.get("latency_ms", {}).values()) if state.get("latency_ms") else None,
        token_usage=state.get("token_usage"),
    )

    if state.get("escalate"):
        convo.status = "escalated"
        db.commit()

    log_turn(
        request_id=request_id,
        session_id=session_id,
        latency_ms=state.get("latency_ms", {}),
        token_usage=state.get("token_usage", {}),
        error=state.get("error"),
    )

    return {
        "request_id": request_id,
        "conversation_id": str(convo.id),
        "response": final_response,
        "sources": citations,
        "tool_result": state.get("tool_result"),
        "confidence": state.get("confidence"),
        "escalated": bool(state.get("escalate")),
        "intent": state.get("intent"),
    }
