"""Domain data models shared across the RAG layers."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from langchain_core.documents import Document


@dataclass(frozen=True)
class Source:
    """A human-readable reference to a retrieved document."""

    name: str
    page: int | None = None

    def __str__(self) -> str:
        page_str = f" (Page {self.page})" if self.page is not None else ""
        return f"{self.name}{page_str}"

    @classmethod
    def from_document(cls, document: Document) -> "Source":
        """Build a :class:`Source` from a LangChain document's metadata."""
        raw_source = document.metadata.get("source", "Unknown")
        name = os.path.basename(raw_source)
        page = document.metadata.get("page")
        # Page metadata is zero-indexed; present it one-indexed to users.
        page_number = page + 1 if isinstance(page, int) else None
        return cls(name=name, page=page_number)


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
        seen: dict[Source, None] = {}
        for document in self.documents:
            seen.setdefault(Source.from_document(document), None)
        return list(seen)


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