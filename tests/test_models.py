"""Tests for domain models."""

from __future__ import annotations

from langchain_core.documents import Document

from src.models import RetrievalResult, Source


def test_source_from_document_normalizes_name_and_page() -> None:
    doc = Document(page_content="x", metadata={"source": "/a/b/guide.pdf", "page": 4})
    source = Source.from_document(doc)
    assert source.name == "guide.pdf"
    assert source.page == 5  # zero-indexed metadata presented one-indexed


def test_source_without_page() -> None:
    doc = Document(page_content="x", metadata={"source": "notes.txt"})
    assert Source.from_document(doc).page is None


def test_retrieval_result_sources_are_deduplicated_and_ordered() -> None:
    docs = [
        Document(page_content="1", metadata={"source": "a.pdf", "page": 0}),
        Document(page_content="2", metadata={"source": "a.pdf", "page": 0}),
        Document(page_content="3", metadata={"source": "b.txt"}),
    ]
    result = RetrievalResult(standalone_question="q", documents=docs)
    sources = result.sources
    assert len(sources) == 2
    assert str(sources[0]) == "a.pdf (Page 1)"
    assert str(sources[1]) == "b.txt"