"""Unit tests for individual tools — validation logic is the important part."""
from app.tools.order_tools import get_order_status, cancel_order
from app.tools.refund_tools import request_refund


def test_get_order_status_found(db_session):
    result = get_order_status(db_session, "ORD-1001")
    assert result["found"] is True
    assert result["status"] == "processing"


def test_get_order_status_not_found(db_session):
    result = get_order_status(db_session, "ORD-9999")
    assert result["found"] is False


def test_cancel_order_success(db_session):
    result = cancel_order(db_session, "ORD-1001")
    assert result["success"] is True
    assert result["status"] == "cancelled"


def test_cancel_order_blocked_when_already_shipped(db_session):
    """Order ORD-1002 is 'shipped' -> must not be cancellable."""
    result = cancel_order(db_session, "ORD-1002")
    assert result["success"] is False
    assert "cannot be cancelled" in result["error"]


def test_request_refund_requires_reason(db_session):
    result = request_refund(db_session, "ORD-1001", reason="no")
    assert result["success"] is False


def test_request_refund_success(db_session):
    result = request_refund(db_session, "ORD-1001", reason="Item arrived damaged")
    assert result["success"] is True
    assert result["refund_status"] == "pending_review"
