"""
Embedding generation.

WHY sentence-transformers locally: it avoids per-call API cost/latency for
embeddings (which run far more often than generation calls, once per chunk
at index time and once per query at retrieval time), and keeps the RAG
pipeline runnable offline/in tests without hitting an external API.
Swap EMBEDDING_MODEL in settings to use an API-based embedding model in
production if higher quality is needed.
"""
from functools import lru_cache
from typing import List

from app.config.settings import get_settings

settings = get_settings()


@lru_cache
def _get_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.EMBEDDING_MODEL)


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Batch-embed texts. Batching amortizes model call overhead vs one-by-one."""
    model = _get_model()
    vectors = model.encode(texts, batch_size=32, show_progress_bar=False, normalize_embeddings=True)
    return vectors.tolist()


def embed_query(text: str) -> List[float]:
    return embed_texts([text])[0]
