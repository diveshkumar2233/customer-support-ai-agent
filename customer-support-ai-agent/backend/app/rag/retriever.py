"""
Retrieval orchestration: embed query -> vector search -> (optional) rerank.

WHY A SEPARATE RERANK STEP: vector similarity alone is approximate. A
lightweight lexical-overlap rerank pass (or a cross-encoder in a bigger
production system) fixes cases where the top vector hit is topically similar
but doesn't actually answer the question. We keep it simple/dependency-free
here with a keyword-overlap boost so the project stays runnable without a
second heavy model, while explaining where a cross-encoder would slot in.
"""
from dataclasses import dataclass
from typing import List

from app.config.settings import get_settings
from app.rag.embeddings import embed_query
from app.rag.vectorstore import VectorStore

settings = get_settings()


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    title: str
    source_path: str
    score: float


def _keyword_overlap_boost(query: str, text: str) -> float:
    q_words = set(w.lower() for w in query.split() if len(w) > 3)
    t_words = set(w.lower() for w in text.split() if len(w) > 3)
    if not q_words:
        return 0.0
    overlap = len(q_words & t_words) / len(q_words)
    return overlap * 0.1  # small boost, vector score still dominates


class Retriever:
    def __init__(self, store: VectorStore | None = None):
        self.store = store or VectorStore()

    def retrieve(self, query: str, top_k: int | None = None) -> List[RetrievedChunk]:
        top_k = top_k or settings.RETRIEVAL_TOP_K
        query_vec = embed_query(query)
        # over-fetch then rerank down to top_k
        raw_hits = self.store.query(query_vec, top_k=max(top_k * 2, top_k))

        reranked = []
        for hit in raw_hits:
            boosted_score = hit["score"] + _keyword_overlap_boost(query, hit["text"])
            reranked.append(
                RetrievedChunk(
                    chunk_id=hit["chunk_id"],
                    text=hit["text"],
                    title=hit["metadata"]["title"],
                    source_path=hit["metadata"]["source_path"],
                    score=boosted_score,
                )
            )
        reranked.sort(key=lambda c: c.score, reverse=True)
        return reranked[:top_k]


# Example input:  retriever.retrieve("Can I get a refund after 30 days?")
# Example output: [RetrievedChunk(title='Refund Policy', score=0.83, text='...'), ...]
