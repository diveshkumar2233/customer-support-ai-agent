# RAG Pipeline

```
documents/*.md -> load_documents() -> clean_text()
                -> chunk_documents() [~900 chars, 150 overlap, sentence-aware]
                -> embed_texts() [sentence-transformers, batched]
                -> VectorStore.upsert_chunks() [Chroma, cosine similarity]

query -> embed_query() -> VectorStore.query() [over-fetch 2x top_k]
       -> keyword-overlap rerank -> top_k RetrievedChunk objects
       -> passed into generation prompt with citation formatting
```

Design choices and trade-offs are documented inline in
`backend/app/rag/chunker.py` and `backend/app/rag/retriever.py` — read those
docstrings for the "why" behind chunk size, overlap, and the lightweight
rerank step.
