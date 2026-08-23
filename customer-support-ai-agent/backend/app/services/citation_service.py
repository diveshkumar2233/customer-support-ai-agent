"""Formats retrieved sources into citation objects for the API response."""


def format_citations(sources: list[dict]) -> list[dict]:
    seen = set()
    citations = []
    for s in sources:
        if s["title"] in seen:
            continue
        seen.add(s["title"])
        citations.append({"title": s["title"], "source": s["source"]})
    return citations
