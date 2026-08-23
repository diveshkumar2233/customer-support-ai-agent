"""
Vector store wrapper (ChromaDB, embedded/local).

WHY Chroma: zero-ops embedded vector DB good for a portfolio project and
local dev; the retriever interface below is provider-agnostic so swapping
in Pinecone/Weaviate/pgvector in production only requires changing this
file, not the agent or API layers.
"""
from typing import List, Dict, Any
import chromadb

from app.config.settings import get_settings
from app.rag.chunker import Chunk

settings = get_settings()


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
        self.collection = self.client.get_or_create_collection(
            name=settings.VECTOR_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_chunks(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        self.collection.upsert(
            ids=[c.chunk_id for c in chunks],
            embeddings=embeddings,
            documents=[c.text for c in chunks],
            metadatas=[
                {"doc_id": c.doc_id, "title": c.title, "source_path": c.source_path} for c in chunks
            ],
        )

    def query(self, query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        result = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        hits = []
        for i in range(len(result["ids"][0])):
            hits.append(
                {
                    "chunk_id": result["ids"][0][i],
                    "text": result["documents"][0][i],
                    "metadata": result["metadatas"][0][i],
                    # Chroma returns distance; convert to a 0-1 similarity score
                    "score": 1 - result["distances"][0][i],
                }
            )
        return hits

    def count(self) -> int:
        return self.collection.count()
