"""
Runs the full evaluation suite over the test dataset and writes results.

Tracks: faithfulness, context relevance, retrieval quality (top-1 hit rate
proxy), tool selection accuracy, latency, and estimated cost — persisted to
the evaluation_results table so trends are visible over time (a key LLMOps
practice: evaluation should be continuous, not a one-off script).
"""
import time

from sqlalchemy.orm import Session

from app.agents.graph import run_agent
from app.evaluation.dataset import load_eval_dataset
from app.evaluation.metrics import score_faithfulness, score_context_relevance
from app.models.ticket import EvaluationResult
from app.services.monitoring_service import estimate_cost


def run_evaluation(db: Session, dataset_path: str = "data/evaluation/test_questions.json") -> list[dict]:
    dataset = load_eval_dataset(dataset_path)
    results = []

    for item in dataset:
        start = time.perf_counter()
        state = run_agent(
            query=item["query"], session_id=f"eval-{item['id']}", customer_id=item.get("customer_id"), db=db
        )
        latency_ms = round((time.perf_counter() - start) * 1000, 2)

        context = "\n".join(c["text"] for c in state.get("retrieved_chunks", []))
        answer = state.get("final_response") or state.get("draft_response") or ""

        faithfulness = score_faithfulness(item["query"], context, answer) if context else None
        relevance = (
            score_context_relevance(item["query"], [c["text"] for c in state.get("retrieved_chunks", [])])
            if state.get("retrieved_chunks")
            else None
        )
        tool_correct = (
            "true" if state.get("planned_tool") == item.get("expected_tool") else "false"
        ) if item.get("expected_tool") else "n/a"

        record = EvaluationResult(
            query=item["query"],
            category=item.get("category", "normal"),
            faithfulness=str(faithfulness.score) if faithfulness else None,
            correctness=None,
            retrieval_relevance=str(relevance.score) if relevance else None,
            tool_selection_correct=tool_correct,
            latency_ms=str(latency_ms),
            notes=answer[:300],
        )
        db.add(record)
        results.append(
            {
                "query": item["query"],
                "category": item.get("category", "normal"),
                "faithfulness": faithfulness.score if faithfulness else None,
                "context_relevance": relevance.score if relevance else None,
                "tool_selection_correct": tool_correct,
                "latency_ms": latency_ms,
                "estimated_cost_usd": estimate_cost(state.get("token_usage", {})),
                "escalated": state.get("escalate", False),
            }
        )

    db.commit()
    return results
