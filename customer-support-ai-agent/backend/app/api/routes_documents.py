"""POST /documents — (re)index the knowledge base into the vector store."""
from fastapi import APIRouter

from app.rag.chunker import chunk_documents
from app.rag.embeddings import embed_texts
from app.rag.loader import load_documents
from app.rag.vectorstore import VectorStore

router = APIRouter(tags=["documents"])


@router.post("/documents/reindex")
def reindex_documents(directory: str = "data/documents"):
    docs = load_documents(directory)
    chunks = chunk_documents(docs)
    if not chunks:
        return {"indexed_documents": 0, "indexed_chunks": 0}

    embeddings = embed_texts([c.text for c in chunks])
    store = VectorStore()
    store.upsert_chunks(chunks, embeddings)
    return {"indexed_documents": len(docs), "indexed_chunks": len(chunks)}
