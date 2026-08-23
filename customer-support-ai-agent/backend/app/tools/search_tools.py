"""Knowledge-base search tool — thin wrapper the agent calls as a 'tool',
even though internally it uses the RAG retriever. Exposing retrieval as a
tool (rather than always-on) lets the agent skip RAG entirely for queries
that don't need it (e.g. 'cancel my order'), saving latency and cost.
"""
from app.rag.retriever import Retriever

_retriever = Retriever()


def search_knowledge_base(query: str, top_k: int = 4) -> dict:
    hits = _retriever.retrieve(query, top_k=top_k)
    return {
        "results": [
            {"title": h.title, "text": h.text, "score": round(h.score, 3), "source": h.source_path}
            for h in hits
        ]
    }
