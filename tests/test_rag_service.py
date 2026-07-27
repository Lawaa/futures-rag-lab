"""Tests for the RagService orchestration layer."""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document

from src.conversation_store import ConversationStore
from src.rag_service import RagService
from src.settings import Settings

from .fakes import RoutingFakeChatModel


class FakeRetriever:
    """Records the last query and returns a fixed document set."""

    def __init__(self, documents: list[Document]) -> None:
        self.documents = documents
        self.last_query: str | None = None

    def invoke(self, query: str):
        self.last_query = query
        return self.documents


def _make_service(
    answer: str, documents: list[Document], **llm_kwargs
) -> tuple[RagService, FakeRetriever]:
    retriever = FakeRetriever(documents)
    llm = RoutingFakeChatModel(answer_response=answer, **llm_kwargs)
    service = RagService(llm=llm, retriever=retriever, settings=Settings())
    return service, retriever


def test_retrieve_translates_query_for_cross_lingual_search() -> None:
    docs = [Document(page_content="ctx", metadata={"source": "a.pdf", "page": 0})]
    service, retriever = _make_service(
        "unused", docs, search_response="what is margin"
    )

    result = service.retrieve("Mi az a letét?", "s1")

    # The graph always prepares a standalone, corpus-language search query.
    assert result.standalone_question == "what is margin"
    assert retriever.last_query == "what is margin"
    assert [str(s) for s in result.sources] == ["a.pdf (Page 1)"]


def test_answer_populates_history_and_returns_sources() -> None:
    docs = [Document(page_content="ctx", metadata={"source": "b.txt"})]
    service, _ = _make_service("Margin is collateral.", docs)

    answer = service.answer("What is margin?", "s1")

    assert answer.text == "Margin is collateral."
    assert answer.grounded is True
    assert [str(s) for s in answer.sources] == ["b.txt"]
    # A user + AI message pair should now be stored.
    assert len(service._history("s1").messages) == 2


def test_disclaimered_answer_drops_local_citations() -> None:
    # When the model falls back to general knowledge it prepends the disclaimer;
    # the local documents did not support the answer, so no citations are shown.
    docs = [Document(page_content="ctx", metadata={"source": "b.txt"})]
    service, _ = _make_service(
        "ℹ️ *Note: not in documents.*\n\nMargin is collateral.", docs
    )

    answer = service.answer("What is margin?", "s1")

    assert answer.grounded is False
    assert answer.sources == []
    assert answer.text.startswith("ℹ️")


def test_groundedness_check_flags_unsupported_answer() -> None:
    # No disclaimer, but the Self-RAG check judges the answer ungrounded: the
    # disclaimer is added and the (false) citations are suppressed.
    docs = [Document(page_content="ctx", metadata={"source": "b.txt"})]
    service, _ = _make_service(
        "The moon is made of cheese.", docs, groundedness_response="no"
    )

    answer = service.answer("What is margin?", "s1")

    assert answer.grounded is False
    assert answer.sources == []
    assert answer.text.startswith("ℹ️")
    assert "cheese" in answer.text


def test_answer_with_no_documents_is_ungrounded() -> None:
    service, _ = _make_service("Any answer.", [])

    answer = service.answer("What is margin?", "s1")

    assert answer.grounded is False
    assert answer.sources == []


def test_groundedness_check_can_be_disabled() -> None:
    docs = [Document(page_content="ctx", metadata={"source": "b.txt"})]
    retriever = FakeRetriever(docs)
    llm = RoutingFakeChatModel(answer_response="Answer.", groundedness_response="no")
    settings = Settings(enable_groundedness_check=False)
    service = RagService(llm=llm, retriever=retriever, settings=settings)

    answer = service.answer("What is margin?", "s1")

    # With the check off, a disclaimer-free answer keeps its citations.
    assert answer.grounded is True
    assert [str(s) for s in answer.sources] == ["b.txt"]


def test_reset_history_clears_session() -> None:
    docs = [Document(page_content="ctx", metadata={"source": "b.txt"})]
    service, _ = _make_service("answer", docs)

    service.answer("q", "s1")
    service.reset_history("s1")

    assert service._history("s1").messages == []


def test_stream_answer_yields_tokens_and_records_history() -> None:
    docs = [Document(page_content="ctx", metadata={"source": "b.txt"})]
    service, _ = _make_service("hello world", docs)

    retrieval = service.retrieve("q", "s1")
    streamed = "".join(service.stream_answer("q", retrieval, "s1"))

    assert streamed == "hello world"
    assert len(service._history("s1").messages) == 2


def _make_service_with_store(
    answer: str, documents: list[Document], store: ConversationStore, **llm_kwargs
) -> RagService:
    retriever = FakeRetriever(documents)
    llm = RoutingFakeChatModel(answer_response=answer, **llm_kwargs)
    return RagService(
        llm=llm, retriever=retriever, settings=Settings(), store=store
    )


def test_answer_persists_conversation_to_store(tmp_path: Path) -> None:
    store = ConversationStore(tmp_path / "conv.sqlite3")
    docs = [Document(page_content="ctx", metadata={"source": "b.txt"})]
    service = _make_service_with_store("Collateral.", docs, store)

    service.answer("What is margin?", "sess-1")

    assert store.load_messages("sess-1") == [
        ("human", "What is margin?"),
        ("ai", "Collateral."),
    ]
    assert [c["id"] for c in service.list_conversations()] == ["sess-1"]


def test_history_resumes_from_store(tmp_path: Path) -> None:
    store = ConversationStore(tmp_path / "conv.sqlite3")
    store.append_turn("sess-1", "earlier question", "earlier answer")

    docs = [Document(page_content="ctx", metadata={"source": "b.txt"})]
    service = _make_service_with_store("unused", docs, store)

    # A fresh service instance rehydrates history from the store on demand.
    messages = service.get_messages("sess-1")
    assert messages == [("human", "earlier question"), ("ai", "earlier answer")]
    assert len(service._history("sess-1").messages) == 2


def test_delete_conversation_removes_from_store(tmp_path: Path) -> None:
    store = ConversationStore(tmp_path / "conv.sqlite3")
    docs = [Document(page_content="ctx", metadata={"source": "b.txt"})]
    service = _make_service_with_store("answer", docs, store)

    service.answer("q", "sess-1")
    service.delete_conversation("sess-1")

    assert service.list_conversations() == []
    assert store.load_messages("sess-1") == []


def test_rename_conversation_updates_store(tmp_path: Path) -> None:
    store = ConversationStore(tmp_path / "conv.sqlite3")
    docs = [Document(page_content="ctx", metadata={"source": "b.txt"})]
    service = _make_service_with_store("answer", docs, store)

    service.answer("q", "sess-1")
    result = service.rename_conversation("sess-1", "Renamed")

    assert result == "Renamed"
    assert service.list_conversations()[0]["title"] == "Renamed"


def test_set_pinned_marks_conversation(tmp_path: Path) -> None:
    store = ConversationStore(tmp_path / "conv.sqlite3")
    docs = [Document(page_content="ctx", metadata={"source": "b.txt"})]
    service = _make_service_with_store("answer", docs, store)

    service.answer("q", "sess-1")

    assert service.set_pinned("sess-1", True) is True
    assert service.list_conversations()[0]["pinned"] is True