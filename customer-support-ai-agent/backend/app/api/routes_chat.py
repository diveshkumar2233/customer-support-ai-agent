"""POST /chat — the primary agent entry point."""
from fastapi import APIRouter, Depends, Request

from app.api.schemas import ChatRequest, ChatResponse
from app.database.session import get_db
from app.security.permissions import enforce_rate_limit
from app.services.chat_service import handle_chat_turn

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request, db=Depends(get_db)):
    enforce_rate_limit(client_key=payload.session_id or request.client.host)
    result = handle_chat_turn(
        db=db, session_id=payload.session_id, customer_id=payload.customer_id, query=payload.message
    )
    return result
