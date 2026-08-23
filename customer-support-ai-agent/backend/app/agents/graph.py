"""
LangGraph wiring: this is the "agent loop" described in the architecture doc.

    User Input
      -> check_input_safety   (guardrail)
      -> classify_intent      (reason/decide)
      -> [retrieve_knowledge]  (conditional: only if intent needs RAG)
      -> [execute_tool]        (conditional: only if intent needs a tool)
      -> generate_response     (grounded generation)
      -> validate_and_score    (confidence/safety check)
      -> [human_handoff]       (conditional: only if escalate=True or error)
      -> END

WHY LangGraph over a plain chain: the branching above (skip retrieval for
"cancel my order", skip tool execution for "what's your refund policy",
loop to human handoff only when needed) is genuine conditional control flow,
not a fixed pipeline. LangGraph models this explicitly as a graph with
conditional edges, which is what makes this "agentic" rather than a linear
RAG chain, and it gives us per-node observability (state after every node)
for free.
"""
from functools import partial

from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from app.agents.nodes import (
    check_input_safety,
    classify_intent,
    retrieve_knowledge,
    execute_tool,
    generate_response,
    validate_and_score,
    human_handoff,
)
from app.agents.state import AgentState


def _route_after_safety(state: AgentState) -> str:
    return "END" if state.get("error") == "prompt_injection_blocked" else "classify_intent"


def _route_after_intent(state: AgentState) -> str:
    if state.get("needs_retrieval"):
        return "retrieve_knowledge"
    if state.get("needs_tool"):
        return "execute_tool"
    return "generate_response"


def _route_after_retrieval(state: AgentState) -> str:
    return "execute_tool" if state.get("needs_tool") else "generate_response"


def _route_after_validation(state: AgentState) -> str:
    return "human_handoff" if state.get("escalate") or state.get("error") else "END"


def build_agent_graph(db: Session):
    """Build (and compile) the LangGraph state machine. `db` is closed over
    for nodes that need DB access (execute_tool, human_handoff)."""
    graph = StateGraph(AgentState)

    graph.add_node("check_input_safety", check_input_safety)
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("retrieve_knowledge", retrieve_knowledge)
    graph.add_node("execute_tool", partial(execute_tool, db=db))
    graph.add_node("generate_response", generate_response)
    graph.add_node("validate_and_score", validate_and_score)
    graph.add_node("human_handoff", partial(human_handoff, db=db))

    graph.set_entry_point("check_input_safety")

    graph.add_conditional_edges(
        "check_input_safety", _route_after_safety, {"classify_intent": "classify_intent", "END": END}
    )
    graph.add_conditional_edges(
        "classify_intent",
        _route_after_intent,
        {
            "retrieve_knowledge": "retrieve_knowledge",
            "execute_tool": "execute_tool",
            "generate_response": "generate_response",
        },
    )
    graph.add_conditional_edges(
        "retrieve_knowledge",
        _route_after_retrieval,
        {"execute_tool": "execute_tool", "generate_response": "generate_response"},
    )
    graph.add_edge("execute_tool", "generate_response")
    graph.add_edge("generate_response", "validate_and_score")
    graph.add_conditional_edges(
        "validate_and_score", _route_after_validation, {"human_handoff": "human_handoff", "END": END}
    )
    graph.add_edge("human_handoff", END)

    return graph.compile()


def run_agent(query: str, session_id: str, customer_id: str | None, db: Session) -> AgentState:
    app = build_agent_graph(db)
    initial_state: AgentState = {
        "query": query,
        "session_id": session_id,
        "customer_id": customer_id,
        "conversation_history": [],
        "planned_tool_args": {"order_id": customer_id or ""},
        "latency_ms": {},
        "token_usage": {},
    }
    final_state = app.invoke(initial_state)
    return final_state
