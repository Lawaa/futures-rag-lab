"""Tests for the RagService orchestration layer."""

from __future__ import annotations

from langchain_core.documents import Document
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from src.rag_service import RagService
from src.settings import Settings


class FakeRetriever:
    """Records the last query and returns a fixed document set."""

    def __init__(self, documents: list[Document]) -> None:
        self.documents = documents
        self.last_query: str | None = None

    def invoke(self, query: str):
        self.last_query = query
        return self.documents


def _make_service(llm_messages: list[AIMessage], documents: list[Document]) -> tuple[RagService, FakeRetriever]:
    retriever = FakeRetriever(documents)
    llm = GenericFakeChatModel(messages=iter(llm_messages))
    service = RagService(llm=llm, retriever=retriever, settings=Settings())
    return service, retriever


def test_retrieve_without_history_uses_raw_question() -> None:
    docs = [Document(page_content="ctx", metadata={"source": "a.pdf", "page": 0})]
    service, retriever = _make_service([AIMessage("unused")], docs)

    result = service.retrieve("What is margin?", "s1")

    assert result.standalone_question == "What is margin?"
    assert retriever.last_query == "What is margin?"
    assert [str(s) for s in result.sources] == ["a.pdf (Page 1)"]


def test_answer_populates_history_and_returns_sources() -> None:
    docs = [Document(page_content="ctx", metadata={"source": "b.txt"})]
    service, _ = _make_service([AIMessage("Margin is collateral.")], docs)

    answer = service.answer("What is margin?", "s1")

    assert answer.text == "Margin is collateral."
    assert [str(s) for s in answer.sources] == ["b.txt"]
    # A user + AI message pair should now be stored.
    assert len(service._history("s1").messages) == 2


def test_reset_history_clears_session() -> None:
    docs = [Document(page_content="ctx", metadata={"source": "b.txt"})]
    service, _ = _make_service([AIMessage("answer")], docs)

    service.answer("q", "s1")
    service.reset_history("s1")

    assert service._history("s1").messages == []


def test_stream_answer_yields_tokens_and_records_history() -> None:
    docs = [Document(page_content="ctx", metadata={"source": "b.txt"})]
    service, _ = _make_service([AIMessage("hello world")], docs)

    retrieval = service.retrieve("q", "s1")
    streamed = "".join(service.stream_answer("q", retrieval, "s1"))

    assert streamed == "hello world"
    assert len(service._history("s1").messages) == 2