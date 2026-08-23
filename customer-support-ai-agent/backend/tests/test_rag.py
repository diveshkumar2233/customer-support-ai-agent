"""RAG pipeline tests: chunking + loading behave as expected without needing a live model."""
from app.rag.chunker import chunk_document
from app.rag.loader import RawDocument, clean_text


def test_clean_text_collapses_whitespace():
    dirty = "Line one\r\n\r\n\r\nLine two   with   spaces"
    cleaned = clean_text(dirty)
    assert "\r" not in cleaned
    assert "\n\n\n" not in cleaned


def test_chunk_document_respects_size_bounds():
    doc = RawDocument(doc_id="test", title="Test", content="Sentence. " * 300, source_path="x.md")
    chunks = chunk_document(doc, chunk_size=200, overlap=30)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c.text) <= 320  # size + small overrun allowed for sentence boundary extension


def test_chunk_ids_are_unique():
    doc = RawDocument(doc_id="test", title="Test", content="A. " * 200, source_path="x.md")
    chunks = chunk_document(doc)
    ids = [c.chunk_id for c in chunks]
    assert len(ids) == len(set(ids))
