# Security

- **Prompt injection / jailbreak detection** (`security/prompt_injection.py`):
  pattern + heuristic pre-filter that blocks the request before it reaches
  the LLM. Defense-in-depth alongside a hardened system prompt.
- **Output guardrails** (`security/guardrails.py`): redacts anything that
  looks like a secret (API keys, card numbers) before a response is sent,
  and enforces the confidence-based escalation policy.
- **Authorization** (`security/guardrails.check_unauthorized_action`):
  blocks any tool call that targets a different customer than the
  authenticated session (IDOR protection).
- **Auth** (`security/auth.py`): stateless JWT bearer tokens.
- **Rate limiting** (`security/permissions.py`): sliding-window limiter per
  session/IP; in-memory for the demo, Redis-backed in production.
- **Secrets**: never hardcoded; loaded via `pydantic-settings` from
  environment variables / `.env` (see `.env.example`).
- **Never expose**: system prompt, internal instructions, API keys, other
  customers' data. Enforced by the system prompt, the guardrail layer, and
  the "never return raw DB rows to the LLM" convention in the tools layer.
