# Resume Project Entry

## Project Title
**Production-Ready Customer Support AI Agent**

## Resume Bullet Points

- Designed and built an **Agentic AI** customer-support system using
  **LangGraph** to orchestrate a multi-step reasoning loop (intent
  classification, conditional **RAG** retrieval, dynamic **tool calling**,
  confidence-based human handoff) instead of a static chatbot pipeline.

- Implemented a full **RAG** pipeline (chunking, batched **embeddings**, and
  a **vector database** with similarity + keyword rerank) to ground LLM
  responses in company policy documents with inline source citations,
  reducing hallucination risk.

- Built a **FastAPI** + **PostgreSQL** backend exposing REST APIs for chat,
  order management, refunds, and ticketing, with JWT auth, rate limiting,
  and **guardrails** against prompt injection, unauthorized cross-customer
  actions, and secret leakage.

- Established an **LLMOps** evaluation framework (faithfulness, context
  relevance, tool-selection accuracy, latency, and token/cost tracking) over
  a 30-query test set spanning normal, ambiguous, and adversarial cases, and
  containerized the full stack with **Docker** for reproducible deployment.

---

*Note: no performance metrics (accuracy %, latency numbers, cost savings)
are included above, since this repository ships without a live deployment
history. Run the evaluation suite (`docs/... evaluator.py`) against your own
API key and traffic, then add real, measured numbers to these bullets —
don't invent them.*
