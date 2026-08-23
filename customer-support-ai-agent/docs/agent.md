# Agent Workflow

The agent loop, implemented as a LangGraph `StateGraph` in
`backend/app/agents/graph.py`:

```
User Input
  -> check_input_safety      (block prompt injection before any LLM call)
  -> classify_intent         (reason/decide: what does the customer want?)
  -> [retrieve_knowledge]    (conditional: only for policy/FAQ-type intents)
  -> [execute_tool]          (conditional: only for order/refund/cancel intents)
  -> generate_response       (grounded strictly in retrieved context + tool output)
  -> validate_and_score      (LLM-judged confidence; below threshold -> escalate)
  -> [human_handoff]         (conditional: creates a ticket, hands off)
  -> END
```

Every node returns a partial state update that LangGraph merges into the
shared `AgentState`, so the full reasoning trace (intent, retrieved chunks,
tool calls, confidence, latency per node, token usage per node) is available
for logging and evaluation without extra instrumentation.
