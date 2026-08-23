# API Reference

Base path: `/api/v1`

## POST /chat
Send a customer message and receive a grounded, guardrailed agent response.

Request:
```json
{ "session_id": "abc123", "customer_id": "CUST-001", "message": "What's your refund policy?" }
```

Response:
```json
{
  "request_id": "…",
  "conversation_id": "…",
  "response": "According to the Refund Policy, ...",
  "sources": [{"title": "Refund Policy", "source": "data/documents/refund_policy.md"}],
  "tool_result": null,
  "confidence": 0.87,
  "escalated": false,
  "intent": "refund"
}
```

## POST /documents/reindex
Re-chunks and re-embeds every document in `data/documents/` into the vector store.

## GET /orders/{order_id}
Returns order status.

## POST /tickets
Creates a support ticket.

## POST /refund
Requests a refund for an order (validated: order must exist and be refundable).

## POST /escalate
Escalates the current conversation to a human, creating a high-priority ticket.

## GET /health
Liveness/readiness check used by orchestrators and load balancers.
