"""
Tool registry: maps tool name -> (function, JSON schema, sensitivity level).

WHY a registry: the agent needs (a) machine-readable schemas to hand to the
LLM's tool-use API, and (b) a single source of truth so adding a new tool
doesn't require touching agent logic. `sensitive=True` tools require the
extra confirmation step in the agent graph before execution.
"""
from app.tools.order_tools import get_order_status, cancel_order
from app.tools.customer_tools import get_customer_details
from app.tools.refund_tools import request_refund, check_refund_status
from app.tools.ticket_tools import create_support_ticket, escalate_to_human
from app.tools.search_tools import search_knowledge_base

TOOL_REGISTRY = {
    "get_order_status": {
        "fn": get_order_status,
        "sensitive": False,
        "schema": {
            "name": "get_order_status",
            "description": "Look up the current status of a customer order by order number.",
            "input_schema": {
                "type": "object",
                "properties": {"order_id": {"type": "string"}},
                "required": ["order_id"],
            },
        },
    },
    "cancel_order": {
        "fn": cancel_order,
        "sensitive": True,
        "schema": {
            "name": "cancel_order",
            "description": "Cancel an order. Requires the order to be in a cancellable state.",
            "input_schema": {
                "type": "object",
                "properties": {"order_id": {"type": "string"}},
                "required": ["order_id"],
            },
        },
    },
    "get_customer_details": {
        "fn": get_customer_details,
        "sensitive": False,
        "schema": {
            "name": "get_customer_details",
            "description": "Fetch non-sensitive customer profile details.",
            "input_schema": {
                "type": "object",
                "properties": {"customer_id": {"type": "string"}},
                "required": ["customer_id"],
            },
        },
    },
    "request_refund": {
        "fn": request_refund,
        "sensitive": True,
        "schema": {
            "name": "request_refund",
            "description": "Request a refund for an order, with a reason.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["order_id", "reason"],
            },
        },
    },
    "check_refund_status": {
        "fn": check_refund_status,
        "sensitive": False,
        "schema": {
            "name": "check_refund_status",
            "description": "Check the status of a previously requested refund.",
            "input_schema": {
                "type": "object",
                "properties": {"order_id": {"type": "string"}},
                "required": ["order_id"],
            },
        },
    },
    "create_support_ticket": {
        "fn": create_support_ticket,
        "sensitive": False,
        "schema": {
            "name": "create_support_ticket",
            "description": "Create a support ticket for an issue that needs manual follow-up.",
            "input_schema": {
                "type": "object",
                "properties": {"issue": {"type": "string"}},
                "required": ["issue"],
            },
        },
    },
    "escalate_to_human": {
        "fn": escalate_to_human,
        "sensitive": False,
        "schema": {
            "name": "escalate_to_human",
            "description": "Escalate the conversation to a human support agent.",
            "input_schema": {
                "type": "object",
                "properties": {"reason": {"type": "string"}},
                "required": ["reason"],
            },
        },
    },
    "search_knowledge_base": {
        "fn": search_knowledge_base,
        "sensitive": False,
        "schema": {
            "name": "search_knowledge_base",
            "description": "Search company policy/FAQ documents for information relevant to the query.",
            "input_schema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
}


def get_tool_schemas() -> list[dict]:
    return [meta["schema"] for meta in TOOL_REGISTRY.values()]
