"""
Order-related tools the agent can call.

WHY tools are separate pure functions: the agent (LangGraph) calls these by
name with structured args produced by the LLM's tool-use output. Keeping
them as plain, independently-testable functions (not embedded in prompt
strings) is what makes this "agentic" rather than a scripted chatbot, and
makes each tool unit-testable in isolation (see tests/test_tools.py).
"""
from sqlalchemy.orm import Session

from app.models.order import Order


def get_order_status(db: Session, order_id: str) -> dict:
    """Look up an order's current status by order_number."""
    order = db.query(Order).filter(Order.order_number == order_id).first()
    if not order:
        return {"found": False, "error": f"No order found with id {order_id}"}
    return {
        "found": True,
        "order_number": order.order_number,
        "status": order.status,
        "total_amount": order.total_amount,
        "is_cancellable": order.is_cancellable,
        "is_refundable": order.is_refundable,
    }


def cancel_order(db: Session, order_id: str) -> dict:
    """
    Cancel an order.
    VALIDATION: only orders in a cancellable state can be cancelled. This
    guards against the agent (or a manipulated prompt) cancelling an order
    that has already shipped.
    """
    order = db.query(Order).filter(Order.order_number == order_id).first()
    if not order:
        return {"success": False, "error": f"No order found with id {order_id}"}
    if order.status in ("shipped", "delivered", "cancelled"):
        return {
            "success": False,
            "error": f"Order {order_id} cannot be cancelled (current status: {order.status})",
        }
    if not order.is_cancellable:
        return {"success": False, "error": f"Order {order_id} is not eligible for cancellation"}

    order.status = "cancelled"
    db.commit()
    return {"success": True, "order_number": order_id, "status": "cancelled"}


# Example input:  get_order_status(db, "ORD-1001")
# Example output: {"found": True, "order_number": "ORD-1001", "status": "processing", ...}
