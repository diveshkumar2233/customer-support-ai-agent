# Interview Questions & Answers — Customer Support AI Agent

### 1. Why did you use RAG instead of just fine-tuning the model on your policies?
Policies change often (refund windows, shipping fees). Fine-tuning would require
retraining every time a policy updates. RAG lets you update a document and
re-index — the model always answers from current, ground-truth text, and every
claim is traceable to a source, which fine-tuned knowledge isn't.

### 2. Why Agentic AI instead of a single RAG chain?
Support requires more than answering FAQ questions — it needs to decide whether
retrieval is even needed, choose and validate a tool (cancel/refund), and know
when to escalate. That's genuine conditional control flow, not a fixed
retrieve-then-generate pipeline, which is what makes it "agentic."

### 3. Why LangGraph specifically?
It models the agent as an explicit state machine with conditional edges, so the
branching logic (skip retrieval for order actions, skip tools for FAQ
questions, escalate on low confidence) is visible and testable as graph
routing functions, rather than buried in nested if/else prompt logic.

### 4. Walk me through what happens when a user says "cancel my order #12345."
Input safety check passes → intent classified as `cancellation` → since that
intent doesn't need retrieval, we skip straight to tool execution →
`cancel_order` validates the order exists and is in a cancellable state before
mutating anything → response generation grounds its reply in the tool result →
confidence check runs → if confident, respond directly; if not, escalate.

### 5. How does tool calling work in this system?
Each tool is a plain Python function registered in `tools/registry.py` with a
JSON schema describing its name, description, and expected arguments. The
agent's intent-classification step maps intent to a planned tool; in a full
production version, the LLM's native tool-use API would extract the arguments
directly from the conversation rather than a simplified mapping.

### 6. How does the agent decide whether a tool call is safe to execute?
Two layers: (1) each tool has its own business-rule validation (e.g. can't
cancel a shipped order), and (2) a guardrail checks the requested
customer/order actually belongs to the authenticated session before any
sensitive tool runs, blocking cross-customer (IDOR-style) requests.

### 7. How does memory work here?
Short-term: the last N turns of a conversation are pulled from Postgres and
included in the prompt window (bounded to control cost/latency). Long-term:
the full conversation history is persisted to the `messages` table regardless,
so a human agent reviewing an escalation sees everything, even if the LLM
prompt itself only sees a recent window.

### 8. How do you prevent hallucinations?
Three mechanisms: (1) the system prompt explicitly forbids inventing policy or
customer data, (2) generation is grounded — the prompt only contains retrieved
context and tool results, nothing else, (3) a confidence-scoring step
LLM-judges whether the answer is actually supported by that context, and
routes to human escalation if not.

### 9. How do you evaluate a RAG system without labeled gold answers?
LLM-as-judge scoring: ask a model to rate faithfulness (is every claim
supported by the retrieved context?) and context relevance (did retrieval
fetch the right chunks?) on a 0-1 scale. It's not as rigorous as human-labeled
correctness, but it's a practical way to get continuous signal without
building a large annotated dataset first — and it's what the evaluator module
does here, over a 30-query test set spanning normal/ambiguous/adversarial/edge
cases.

### 10. How do you handle prompt injection?
A pattern + heuristic pre-filter (`security/prompt_injection.py`) checks the
raw user input for known attack shapes (instruction override, jailbreak
role-play, system-prompt extraction attempts) *before* it reaches the LLM.
This is defense-in-depth alongside a hardened system prompt — neither alone is
sufficient.

### 11. What's the difference between your input guardrail and output guardrail?
The input guardrail (`prompt_injection.py`) blocks malicious *requests* before
any model call. The output guardrail (`guardrails.py`) redacts anything
secret-shaped from the *response* and enforces the confidence-based escalation
policy — it's the last line of defense right before a user sees a response.

### 12. How would you scale this to thousands of concurrent users?
The backend is stateless (JWT auth, no server-side session), so it scales
horizontally behind a load balancer. Postgres uses connection pooling per
instance; at higher scale you'd add pgbouncer. The vector store would move
from embedded Chroma to a managed/clustered vector DB. Rate limiting would
move from in-memory to Redis so limits apply across replicas.

### 13. How do you reduce LLM cost in a system like this?
Skip retrieval/tool calls entirely when intent doesn't need them (conditional
graph edges), keep the memory window bounded rather than replaying full
history, use a cheaper/faster model for the intent-classification and
confidence-scoring steps versus the main generation step, and cache frequent
FAQ-style queries.

### 14. How do you handle LLM API failures?
The tool-execution node wraps calls in try/except and returns a structured
failure rather than crashing the graph; a global FastAPI exception handler
prevents stack traces leaking to the client. In production you'd add retry
with exponential backoff and a timeout, then fall back to the human-handoff
path if retries are exhausted.

### 15. Why a vector database instead of just keyword search?
Vector search finds semantically similar text even when the customer's
phrasing doesn't match the policy document's wording (e.g. "can I send it
back" vs. "return policy"). We combine it with a lightweight keyword-overlap
rerank to catch cases where pure vector similarity misses an exact-term match.

### 16. How does chunk size affect retrieval quality?
Chunks too large dilute the embedding across unrelated sentences, hurting
precision. Chunks too small lose surrounding context needed to fully answer a
question, hurting recall. We use ~900 characters with 150-character overlap
for these policy documents, extending to the nearest sentence boundary to
avoid cutting mid-sentence.

### 17. What would a cross-encoder reranker add over your current rerank step?
A cross-encoder jointly scores the (query, chunk) pair through a shared model,
capturing interaction between them that separate embeddings can't. Our
current keyword-overlap boost is a cheap, dependency-light approximation;
swapping in a cross-encoder (e.g. `ms-marco-MiniLM`) would improve precision
at the cost of extra inference latency per query.

### 18. How do you decide when to escalate to a human?
An LLM-judged confidence score on the generated answer, checked against a
threshold (`CONFIDENCE_THRESHOLD`). Below threshold, the fallback message is
returned and a support ticket is auto-created via `escalate_to_human`, so
escalation always leaves an auditable trail rather than silently failing.

### 19. Why store tool_actions as a separate audit table?
So every sensitive action the agent takes (cancel, refund) is independently
traceable outside the chat transcript — critical for debugging disputed
actions and for compliance/audit requirements in a real support system.

### 20. How would you add streaming responses?
Switch the `/chat` endpoint to return a `StreamingResponse` (SSE), and have
the generation node yield tokens as they arrive from the provider's streaming
API (Groq and Gemini both support streaming) instead of waiting for the full completion — the rest of the graph
(retrieval, tool execution) stays synchronous since only the final generation
step benefits from streaming.

### 21. How do you keep customer data from leaking into logs?
Structured logs record request IDs, latency, and token usage — not raw
message content or tool payloads. Tools that touch PII (e.g.
`get_customer_details`) mask sensitive fields (like email) before returning
them to the LLM, so even the model's own context never holds the full secret.

### 22. Why Pydantic Settings instead of `os.environ` calls scattered in the code?
Centralizes and type-validates every config value in one place, fails fast on
missing/malformed config at startup rather than at first use, and makes it
obvious what environment variables the app needs (useful for onboarding and
for writing `.env.example`).

### 23. Why SQLAlchemy models instead of raw SQL?
Type-safe schema definitions that double as documentation, easy relationship
traversal (e.g. conversation → messages), and portability — the same models
work with SQLite in tests and Postgres in production without rewriting
queries.

### 24. How do you test an LLM-dependent system deterministically?
Split logic into LLM-independent pure functions wherever possible (routing
functions, validation logic, guardrail regex checks) and unit-test those
without mocking the model. For the parts that do need the LLM (generation,
confidence scoring), tests would mock the `llm_client.generate()` response
rather than hitting the real Groq/Gemini API in CI.

### 25. What's the biggest weakness in the current implementation, and how would you fix it?
Tool-argument extraction currently uses a simplified deterministic mapping
rather than parsing arguments from the LLM's native tool-use response. In
production I'd have the LLM emit structured `tool_use` blocks so multi-slot
arguments (e.g. refund reason plus order id) are extracted directly from
conversation, not guessed from state.

### 26. How does authentication work, and why JWT?
Stateless JWT bearer tokens issued at login; each request's token is verified
against `SECRET_KEY` without a server-side session lookup, which is what lets
any backend replica validate a request independently — necessary for
horizontal scaling.

### 27. How do you prevent one client from overwhelming the system?
A sliding-window rate limiter (`security/permissions.py`) caps requests per
session/IP per minute at the API layer, returning HTTP 429 once exceeded.

### 28. Why separate `services/` from `agents/`?
`agents/` is pure reasoning logic (the LangGraph state machine); `services/`
orchestrates it with side effects — saving messages, formatting citations,
logging. This separation means the agent graph can be tested and reused
independent of how a specific channel (REST API, Slack bot, etc.) wires it up.

### 29. How would you monitor this system after deployment?
Structured JSON logs (request ID, per-node latency, token usage, estimated
cost, errors) shipped to a log aggregator; the `/health` endpoint wired into
container orchestrator liveness checks; the evaluation suite run on a
schedule against the `evaluation_results` table to catch quality regressions
over time, not just at launch.

### 30. What would you change if this needed to support multiple languages?
Keep retrieval embedding-model-agnostic (swap to a multilingual
sentence-transformers model), translate/maintain policy documents per
language rather than relying on the LLM to translate on the fly (to keep
citations accurate to the actual published policy), and make the system
prompt's tone/formality instructions language-aware.
