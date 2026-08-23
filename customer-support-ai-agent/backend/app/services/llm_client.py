"""
Provider-agnostic LLM client.

WHY: every agent node (intent classification, response generation, confidence
scoring) needs to call an LLM, but we don't want that call tied to one
vendor's SDK. This wrapper normalizes Groq and Google Gemini (both of which
offer usable free tiers) behind one interface: `generate(system, user,
max_tokens)` returning `LLMResponse(text, input_tokens, output_tokens)`.
Swapping providers is a one-line config change (`LLM_PROVIDER` in .env),
nothing in agents/nodes.py or evaluation/metrics.py needs to change.
"""
from dataclasses import dataclass

from app.config.settings import get_settings

settings = get_settings()


@dataclass
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int


def _call_groq(system: str, user: str, max_tokens: int) -> LLMResponse:
    from groq import Groq

    client = Groq(api_key=settings.GROQ_API_KEY)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})

    resp = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=settings.LLM_TEMPERATURE,
    )
    choice = resp.choices[0].message.content or ""
    usage = resp.usage
    return LLMResponse(
        text=choice.strip(),
        input_tokens=getattr(usage, "prompt_tokens", 0) or 0,
        output_tokens=getattr(usage, "completion_tokens", 0) or 0,
    )


def _call_gemini(system: str, user: str, max_tokens: int) -> LLMResponse:
    import google.generativeai as genai

    genai.configure(api_key=settings.GOOGLE_API_KEY)
    model = genai.GenerativeModel(
        model_name=settings.GEMINI_MODEL,
        system_instruction=system or None,
    )
    resp = model.generate_content(
        user,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=settings.LLM_TEMPERATURE,
        ),
    )
    text = (resp.text or "").strip()
    usage = getattr(resp, "usage_metadata", None)
    input_tokens = getattr(usage, "prompt_token_count", 0) or 0
    output_tokens = getattr(usage, "candidates_token_count", 0) or 0
    return LLMResponse(text=text, input_tokens=input_tokens, output_tokens=output_tokens)


def generate(system: str, user: str, max_tokens: int | None = None) -> LLMResponse:
    """
    Single entry point every agent node / evaluator calls.
    Routes to whichever provider is configured in settings.LLM_PROVIDER.
    """
    max_tokens = max_tokens or settings.LLM_MAX_TOKENS

    if settings.LLM_PROVIDER == "groq":
        return _call_groq(system, user, max_tokens)
    if settings.LLM_PROVIDER == "gemini":
        return _call_gemini(system, user, max_tokens)

    raise ValueError(
        f"Unsupported LLM_PROVIDER '{settings.LLM_PROVIDER}'. Use 'groq' or 'gemini'."
    )


# Example:
# >>> generate(system="You are a helpful assistant.", user="Say hi in 5 words.")
# LLMResponse(text="Hello there, how can I help?", input_tokens=18, output_tokens=8)
