# Architecture

## Request flow

```
User
 -> Frontend (React)
 -> FastAPI Backend (/api/v1/chat)
 -> Auth + rate limiting + request-id middleware
 -> Chat Service (orchestration)
 -> LangGraph Agent
     -> Input safety guardrail
     -> Intent classification
     -> RAG retrieval (conditional)
     -> Tool execution (conditional, with validation)
     -> Response generation (grounded in retrieval + tool output)
     -> Confidence/safety validation
     -> Human handoff (conditional)
 -> Guardrails (output redaction)
 -> Database (conversation, message, audit logs)
 -> Response back to user
```

## Why this shape

- **Thin API layer, fat service/agent layer**: FastAPI routes only handle HTTP
  concerns (validation, status codes). All business logic lives in `services/`
  and `agents/`, so it can be tested and reused independent of HTTP.
- **Agent as a graph, not a chain**: the agent's control flow is genuinely
  conditional (skip retrieval for "cancel my order", skip tools for "what's
  your refund policy"). LangGraph models this as a state machine with
  conditional edges rather than a fixed sequence of LLM calls.
- **Guardrails at two points**: once on input (prompt injection / jailbreak
  detection, before any LLM call) and once on output (secret redaction,
  confidence-based escalation, before the response reaches the user).
- **Tools are plain, testable functions**: registered in a single
  `tools/registry.py` so the agent, the API routes, and the tests all share
  one source of truth for what a tool does and what its schema is.

## Scaling to thousands of concurrent users

- FastAPI + Uvicorn workers are stateless — horizontal scaling is just
  running more container replicas behind a load balancer.
- Postgres connection pooling (`pool_size`/`max_overflow`) bounds DB
  connections per instance; a pgbouncer layer would be added at higher scale.
- The vector store (Chroma here) would move to a managed/clustered service
  (Pinecone, Weaviate, or pgvector with read replicas) once a single-node
  embedded store becomes the bottleneck.
- Rate limiting is currently in-memory (fine for one instance); production
  would back it with Redis so limits apply across all replicas.
- LLM calls are the long pole on latency — async FastAPI handlers let the
  event loop serve other requests while waiting on the LLM API.
