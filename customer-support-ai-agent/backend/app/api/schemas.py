"""Pydantic request/response schemas — the API's public contract."""
from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Client-generated session/conversation id")
    customer_id: Optional[str] = Field(None, description="Authenticated customer id, if any")
    message: str = Field(..., min_length=1, max_length=2000)


class Citation(BaseModel):
    title: str
    source: str


class ChatResponse(BaseModel):
    request_id: str
    conversation_id: str
    response: str
    sources: list[Citation]
    tool_result: Optional[dict] = None
    confidence: Optional[float] = None
    escalated: bool
    intent: Optional[str] = None


class OrderStatusResponse(BaseModel):
    found: bool
    order_number: Optional[str] = None
    status: Optional[str] = None
    total_amount: Optional[float] = None
    error: Optional[str] = None


class TicketCreateRequest(BaseModel):
    issue: str = Field(..., min_length=5)
    conversation_id: Optional[str] = None
    priority: str = "normal"


class TicketResponse(BaseModel):
    success: bool
    ticket_id: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None


class RefundRequest(BaseModel):
    order_id: str
    reason: str = Field(..., min_length=5)


class RefundResponse(BaseModel):
    success: bool
    order_number: Optional[str] = None
    refund_status: Optional[str] = None
    error: Optional[str] = None


class EscalateRequest(BaseModel):
    reason: str = Field(..., min_length=5)
    conversation_id: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
