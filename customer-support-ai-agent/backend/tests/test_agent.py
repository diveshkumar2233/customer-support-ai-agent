"""
Agent graph routing tests.

These test the CONDITIONAL EDGE LOGIC directly (pure functions), which is
the part of the agent most worth unit-testing without needing to mock the
LLM for every test.
"""
from app.agents.graph import _route_after_intent, _route_after_retrieval, _route_after_validation


def test_routes_to_retrieval_when_needed():
    state = {"needs_retrieval": True, "needs_tool": False}
    assert _route_after_intent(state) == "retrieve_knowledge"


def test_routes_to_tool_when_needed():
    state = {"needs_retrieval": False, "needs_tool": True}
    assert _route_after_intent(state) == "execute_tool"


def test_routes_straight_to_generation_otherwise():
    state = {"needs_retrieval": False, "needs_tool": False}
    assert _route_after_intent(state) == "generate_response"


def test_routes_to_tool_after_retrieval_if_both_needed():
    state = {"needs_tool": True}
    assert _route_after_retrieval(state) == "execute_tool"


def test_routes_to_human_handoff_on_low_confidence():
    state = {"escalate": True}
    assert _route_after_validation(state) == "human_handoff"


def test_routes_to_end_when_confident():
    state = {"escalate": False, "error": None}
    assert _route_after_validation(state) == "END"
