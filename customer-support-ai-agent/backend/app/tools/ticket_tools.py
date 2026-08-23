"""Support-ticket + human-escalation tools."""
from sqlalchemy.orm import Session

from app.models.ticket import SupportTicket


def create_support_ticket(db: Session, issue: str, conversation_id: str | None = None, priority: str = "normal") -> dict:
    ticket = SupportTicket(conversation_id=conversation_id, reason=issue, priority=priority)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return {"success": True, "ticket_id": str(ticket.id), "status": ticket.status, "priority": priority}


def escalate_to_human(db: Session, reason: str, conversation_id: str | None = None) -> dict:
    """
    Escalation is itself implemented as creating a high-priority ticket +
    flagging the conversation, so escalation always leaves an auditable trail.
    """
    ticket = create_support_ticket(db, issue=reason, conversation_id=conversation_id, priority="high")
    return {"success": True, "escalated": True, "ticket_id": ticket["ticket_id"], "reason": reason}
