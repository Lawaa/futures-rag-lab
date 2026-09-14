"""Domain data models shared across the RAG layers."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from langchain_core.documents import Document


import re

SECTION_REGEX = re.compile(r"(\b\d+:\d+\.\s*§|\b\d+\.\s*§)")


@dataclass(frozen=True)
class Source:
    """A human-readable reference to a retrieved document."""

    name: str
    page: int | None = None
    snippet: str | None = None
    highlight_text: str | None = None
    chunk_content: str | None = None
    section_id: str | None = None

    def __str__(self) -> str:
        page_str = f" (Page {self.page})" if self.page is not None else ""
        section_str = f" [{self.section_id}]" if self.section_id is not None else ""
        return f"{self.name}{page_str}{section_str}"

    @classmethod
    def from_document(cls, document: Document) -> "Source":
        """Build a :class:`Source` from a LangChain document's metadata."""
        raw_source = document.metadata.get("source", "Unknown")
        name = os.path.basename(raw_source)
        page = document.metadata.get("page")
        # Page metadata is zero-indexed; present it one-indexed to users.
        page_number = page + 1 if isinstance(page, int) else None
        snippet = document.page_content.strip() if document.page_content else None
        section_id = document.metadata.get("section_id")
        if not section_id and snippet:
            match = SECTION_REGEX.search(snippet)
            if match:
                section_id = match.group(1).strip()
        return cls(
            name=name,
            page=page_number,
            snippet=snippet,
            highlight_text=snippet,
            chunk_content=snippet,
            section_id=section_id,
        )


@dataclass(frozen=True)
class RetrievalResult:
    """The outcome of a retrieval step."""

    standalone_question: str
    documents: list[Document] = field(default_factory=list)
    # Number of self-correction query rewrites performed to reach this result.
    retry_count: int = 0
    # Profile the retrieval graph routed this turn to (None => active profile).
    profile_id: str | None = None

    @property
    def sources(self) -> list[Source]:
        """Deduplicated, ordered list of sources for the retrieved documents."""
        seen: dict[tuple[str, int | None, str | None], Source] = {}
        for document in self.documents:
            src = Source.from_document(document)
            key = (src.name, src.page, src.section_id)
            if key not in seen:
                seen[key] = src
        return list(seen.values())



@dataclass(frozen=True)
class Answer:
    """A generated answer together with its supporting sources.

    ``grounded`` is ``False`` when the answer relies on knowledge outside the
    loaded documents; in that case ``sources`` is empty so the UI never shows
    citations that did not actually support the answer.
    """

    text: str
    sources: list[Source] = field(default_factory=list)
    grounded: bool = True