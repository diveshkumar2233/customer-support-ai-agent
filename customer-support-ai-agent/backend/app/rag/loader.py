"""
Document loading + cleaning.

WHY: Raw source documents (markdown/txt/pdf exports of policies) contain
formatting noise (extra whitespace, headers repeated per page, HTML
artifacts) that hurts embedding quality. Cleaning before chunking gives the
retriever cleaner semantic units to work with.
"""
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class RawDocument:
    doc_id: str
    title: str
    content: str
    source_path: str


def clean_text(text: str) -> str:
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_documents(directory: str) -> List[RawDocument]:
    """Load every .md/.txt file in `directory` into a RawDocument."""
    docs: List[RawDocument] = []
    for path in sorted(Path(directory).glob("*.*")):
        if path.suffix.lower() not in (".md", ".txt"):
            continue
        raw = path.read_text(encoding="utf-8", errors="ignore")
        title = path.stem.replace("_", " ").title()
        docs.append(
            RawDocument(
                doc_id=path.stem,
                title=title,
                content=clean_text(raw),
                source_path=str(path),
            )
        )
    return docs


# Example:
# >>> load_documents("data/documents")
# [RawDocument(doc_id='refund_policy', title='Refund Policy', content='...', source_path='...')]
