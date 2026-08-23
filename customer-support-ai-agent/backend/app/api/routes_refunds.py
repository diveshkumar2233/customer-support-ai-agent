"""POST /refund"""
from fastapi import APIRouter, Depends

from app.api.schemas import EscalateRequest, RefundRequest, RefundResponse
from app.database.session import get_db
from app.tools.refund_tools import request_refund
from app.tools.ticket_tools import escalate_to_human

router = APIRouter(tags=["refunds", "escalation"])


@router.post("/refund", response_model=RefundResponse)
def refund(payload: RefundRequest, db=Depends(get_db)):
    return request_refund(db, order_id=payload.order_id, reason=payload.reason)


@router.post("/escalate")
def escalate(payload: EscalateRequest, db=Depends(get_db)):
    return escalate_to_human(db, reason=payload.reason, conversation_id=payload.conversation_id)
