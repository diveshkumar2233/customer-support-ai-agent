"""POST /tickets"""
from fastapi import APIRouter, Depends

from app.api.schemas import TicketCreateRequest, TicketResponse
from app.database.session import get_db
from app.tools.ticket_tools import create_support_ticket

router = APIRouter(tags=["tickets"])


@router.post("/tickets", response_model=TicketResponse)
def create_ticket(payload: TicketCreateRequest, db=Depends(get_db)):
    return create_support_ticket(
        db, issue=payload.issue, conversation_id=payload.conversation_id, priority=payload.priority
    )
