"""
Evaluation metrics for the RAG + agent pipeline.

WHY these specific metrics (interview-relevant):
- Faithfulness: does the answer only state things supported by the retrieved
  context? (catches hallucination)
- Answer correctness: does it actually answer what was asked, vs. correct-
  but-irrelevant?
- Context relevance: did retrieval fetch the right chunks at all? (separates
  "bad retrieval" from "bad generation" failures)
- Tool selection accuracy: did the agent pick the right tool (or correctly
  pick none)?
We implement these as LLM-judge scorers (cheap to run, don't need labeled
gold answers) — a common pragmatic approach when you don't have a large
human-labeled eval set yet. The judge call goes through the same
provider-agnostic llm_client used by the agent (Groq/Gemini), so evaluation
never needs its own separate API key or SDK.
"""
from dataclasses import dataclass

from app.services import llm_client


@dataclass
class EvalScore:
    score: float  # 0.0 - 1.0
    rationale: str


def _judge(prompt: str) -> EvalScore:
    resp = llm_client.generate(system="", user=prompt, max_tokens=100)
    text = resp.text.strip()
    try:
        score_line, *rest = text.split("\n", 1)
        score = float(score_line.strip().split()[0])
    except (ValueError, IndexError):
        score = 0.5
    return EvalScore(score=max(0.0, min(1.0, score)), rationale=text)


def score_faithfulness(query: str, context: str, answer: str) -> EvalScore:
    prompt = (
        f"Context:\n{context}\n\nAnswer:\n{answer}\n\n"
        "Score 0.0-1.0 how faithful the answer is to the context (1.0 = every claim is "
        "supported by the context, 0.0 = fabricated). Reply with the number then a one-line reason."
    )
    return _judge(prompt)


def score_correctness(query: str, answer: str, expected: str) -> EvalScore:
    prompt = (
        f"Question: {query}\nExpected answer covers: {expected}\nActual answer: {answer}\n\n"
        "Score 0.0-1.0 how well the actual answer covers the expected content. "
        "Reply with the number then a one-line reason."
    )
    return _judge(prompt)


def score_context_relevance(query: str, retrieved_chunks: list[str]) -> EvalScore:
    context = "\n---\n".join(retrieved_chunks)
    prompt = (
        f"Question: {query}\nRetrieved chunks:\n{context}\n\n"
        "Score 0.0-1.0 how relevant the retrieved chunks are to answering the question. "
        "Reply with the number then a one-line reason."
    )
    return _judge(prompt)
