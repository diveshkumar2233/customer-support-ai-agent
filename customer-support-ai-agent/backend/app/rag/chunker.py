"""
Chunking strategy: fixed-size overlapping chunks with sentence-aware boundaries.

WHY CHUNK SIZE MATTERS (interview-relevant): chunks that are too large dilute
the embedding (average meaning across unrelated sentences -> poor retrieval
precision). Chunks that are too small lose context needed to answer the
question (poor recall / broken sentences). Overlap prevents losing meaning
that spans a chunk boundary. We use ~250 tokens (~1000 chars) with 15%
overlap as a reasonable default for short policy documents.
"""
from dataclasses import dataclass
from typing import List

from app.rag.loader import RawDocument


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    text: str
    source_path: str


def chunk_document(doc: RawDocument, chunk_size: int = 900, overlap: int = 150) -> List[Chunk]:
    text = doc.content
    chunks: List[Chunk] = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        # try not to cut mid-sentence: extend to the next period if close by
        if end < len(text):
            next_period = text.find(".", end, end + 100)
            if next_period != -1:
                end = next_period + 1
        piece = text[start:end].strip()
        if piece:
            chunks.append(
                Chunk(
                    chunk_id=f"{doc.doc_id}_{idx}",
                    doc_id=doc.doc_id,
                    title=doc.title,
                    text=piece,
                    source_path=doc.source_path,
                )
            )
            idx += 1
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def chunk_documents(docs: List[RawDocument], **kwargs) -> List[Chunk]:
    all_chunks: List[Chunk] = []
    for doc in docs:
        all_chunks.extend(chunk_document(doc, **kwargs))
    return all_chunks
