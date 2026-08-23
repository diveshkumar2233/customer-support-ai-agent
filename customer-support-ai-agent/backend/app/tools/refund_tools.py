"""Refund tools with eligibility checks before issuing anything."""
from sqlalchemy.orm import Session

from app.models.order import Order


def request_refund(db: Session, order_id: str, reason: str) -> dict:
    """
    VALIDATION CHAIN before a refund is created:
    1. order exists
    2. order.is_refundable
    3. reason is non-trivial (guards against empty/garbage reasons)
    A real system would also check refund_window_days against order age.
    """
    order = db.query(Order).filter(Order.order_number == order_id).first()
    if not order:
        return {"success": False, "error": f"No order found with id {order_id}"}
    if not order.is_refundable:
        return {"success": False, "error": f"Order {order_id} is not eligible for a refund"}
    if not reason or len(reason.strip()) < 5:
        return {"success": False, "error": "Please provide a valid reason for the refund"}

    # In production this would create a Refund row + call a payment provider.
    return {
        "success": True,
        "order_number": order_id,
        "refund_status": "pending_review",
        "reason": reason,
    }


def check_refund_status(db: Session, order_id: str) -> dict:
    order = db.query(Order).filter(Order.order_number == order_id).first()
    if not order:
        return {"found": False, "error": f"No order found with id {order_id}"}
    # Mocked status derivation for the demo
    status = "not_requested" if order.is_refundable else "not_eligible"
    return {"found": True, "order_number": order_id, "refund_status": status}
