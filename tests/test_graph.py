"""Tests for the LangGraph retrieval pipeline (cross-lingual + self-correction)."""

from __future__ import annotations

import threading

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
from pydantic import PrivateAttr

from src.graph import RetrievalGraph
from src.profiles import ProfileRegistry, Profile
from src.settings import Settings

from .fakes import RoutingFakeChatModel


class RecordingRetriever:
    """Returns queued document batches and records every query it sees."""

    def __init__(self, batches: list[list[Document]]) -> None:
        self._batches = batches
        self.queries: list[str] = []

    def invoke(self, query: str):
        self.queries.append(query)
        index = min(len(self.queries) - 1, len(self._batches) - 1)
        return self._batches[index]


class FlippingGraderModel(RoutingFakeChatModel):
    """Grades the first attempt irrelevant, then relevant afterwards."""

    _grade_calls: int = PrivateAttr(default=0)

    def _route(self, messages: list[BaseMessage]) -> str:
        system = messages[0].content.lower() if messages else ""
        if "relevance grader" in system:
            self._grade_calls += 1
            return "no" if self._grade_calls == 1 else "yes"
        return super()._route(messages)


def _doc(text: str) -> Document:
    return Document(page_content=text, metadata={"source": "x.txt"})


def test_prepare_query_translates_into_corpus_language() -> None:
    retriever = RecordingRetriever([[_doc("ctx")]])
    llm = RoutingFakeChatModel(search_response="margin requirements", grade_response="yes")
    graph = RetrievalGraph(llm, retriever, Settings())

    state = graph.run("Mekkora a letét?", [])

    assert state["search_query"] == "margin requirements"
    assert retriever.queries == ["margin requirements"]
    assert state["retry_count"] == 0


def test_self_correction_rewrites_until_relevant() -> None:
    # First retrieval is judged irrelevant, second (after rewrite) is relevant.
    retriever = RecordingRetriever([[_doc("off topic")], [_doc("on topic")]])
    llm = FlippingGraderModel(
        search_response="first query", rewrite_response="better query"
    )
    graph = RetrievalGraph(llm, retriever, Settings())

    state = graph.run("What is margin?", [])

    assert retriever.queries == ["first query", "better query"]
    assert state["retry_count"] == 1
    assert state["relevant"] is True


def test_self_correction_stops_at_retry_budget() -> None:
    retriever = RecordingRetriever([[_doc("never relevant")]])
    llm = RoutingFakeChatModel(
        search_response="q0", grade_response="no", rewrite_response="q-next"
    )
    settings = Settings(max_retrieval_retries=2)
    graph = RetrievalGraph(llm, retriever, settings)

    state = graph.run("What is margin?", [])

    # Initial attempt + 2 rewrites = 3 retrievals, then it gives up.
    assert len(retriever.queries) == 3
    assert state["retry_count"] == 2
    assert state["relevant"] is False


def test_self_correction_can_be_disabled() -> None:
    retriever = RecordingRetriever([[_doc("ctx")]])
    llm = RoutingFakeChatModel(search_response="q0", grade_response="no")
    settings = Settings(enable_self_correction=False)
    graph = RetrievalGraph(llm, retriever, settings)

    state = graph.run("What is margin?", [])

    # No grading or rewriting happens; a single retrieval pass is made.
    assert retriever.queries == ["q0"]
    assert "relevant" not in state


def test_empty_documents_are_graded_irrelevant() -> None:
    retriever = RecordingRetriever([[]])
    llm = RoutingFakeChatModel(search_response="q0", grade_response="yes")
    settings = Settings(max_retrieval_retries=0)
    graph = RetrievalGraph(llm, retriever, settings)

    state = graph.run("What is margin?", [])

    assert state["relevant"] is False


def _two_profiles() -> ProfileRegistry:
    return ProfileRegistry(
        profiles=(
            Profile(id="trading", name="Trading", description="Futures trading"),
            Profile(id="legal", name="Legal", description="Contracts and law"),
        ),
        active_id="trading",
    )


def test_router_selects_profile_when_enabled() -> None:
    retriever = RecordingRetriever([[_doc("ctx")]])
    llm = RoutingFakeChatModel(search_response="q0", router_response="legal")
    settings = Settings(enable_profile_routing=True)
    graph = RetrievalGraph(llm, retriever, settings, _two_profiles())

    state = graph.run("Is this contract binding?", [])

    assert state["profile_id"] == "legal"


def test_router_disabled_leaves_profile_unset() -> None:
    retriever = RecordingRetriever([[_doc("ctx")]])
    llm = RoutingFakeChatModel(search_response="q0", router_response="legal")
    # Routing off by default: the router node is never added.
    graph = RetrievalGraph(llm, retriever, Settings(), _two_profiles())

    state = graph.run("Any question", [])

    assert "profile_id" not in state


def test_router_unknown_choice_falls_back_to_first_profile() -> None:
    retriever = RecordingRetriever([[_doc("ctx")]])
    llm = RoutingFakeChatModel(search_response="q0", router_response="nonsense")
    settings = Settings(enable_profile_routing=True)
    graph = RetrievalGraph(llm, retriever, settings, _two_profiles())

    state = graph.run("Any question", [])

    assert state["profile_id"] == "trading"


class MappingRetriever:
    """Thread-safe retriever returning per-query batches for fan-out tests."""

    def __init__(self, mapping: dict[str, list[Document]]) -> None:
        self._mapping = mapping
        self._lock = threading.Lock()
        self.queries: list[str] = []

    def invoke(self, query: str):
        with self._lock:
            self.queries.append(query)
        return self._mapping.get(query, [])


def test_multi_query_fans_out_and_fuses_results() -> None:
    doc_a, doc_b, doc_c = _doc("alpha"), _doc("beta"), _doc("gamma")
    retriever = MappingRetriever(
        {
            "q0": [doc_a, doc_b],
            "alt query 1": [doc_b, doc_c],
            "alt query 2": [doc_c],
        }
    )
    llm = RoutingFakeChatModel(
        search_response="q0",
        multi_query_response="alt query 1\nalt query 2",
        grade_response="yes",
    )
    settings = Settings(enable_multi_query=True, enable_self_correction=False)
    graph = RetrievalGraph(llm, retriever, settings)

    state = graph.run("What is margin?", [])

    # Original query is kept and expansion variants are added (order-independent).
    assert set(retriever.queries) == {"q0", "alt query 1", "alt query 2"}
    assert state["search_queries"] == ["q0", "alt query 1", "alt query 2"]
    # RRF fuses and de-duplicates; doc_b appears in two lists so it ranks top.
    contents = [doc.page_content for doc in state["documents"]]
    assert contents[0] == "beta"
    assert sorted(contents) == ["alpha", "beta", "gamma"]


def test_multi_query_disabled_keeps_single_query_path() -> None:
    retriever = RecordingRetriever([[_doc("ctx")]])
    llm = RoutingFakeChatModel(search_response="q0", grade_response="yes")
    graph = RetrievalGraph(llm, retriever, Settings())

    state = graph.run("What is margin?", [])

    assert retriever.queries == ["q0"]
    assert "search_queries" not in state


def test_checkpointer_persists_state_across_turns() -> None:
    import sqlite3

    from langgraph.checkpoint.sqlite import SqliteSaver

    conn = sqlite3.connect(":memory:", check_same_thread=False)
    saver = SqliteSaver(conn)
    saver.setup()

    retriever = RecordingRetriever([[_doc("ctx")]])
    llm = RoutingFakeChatModel(search_response="q0", grade_response="yes")
    graph = RetrievalGraph(llm, retriever, Settings(), checkpointer=saver)

    graph.run("First question", [], session_id="conv-1")

    # A checkpoint was written for the conversation thread.
    checkpoint = saver.get({"configurable": {"thread_id": "conv-1"}})
    assert checkpoint is not None

    # Deleting the thread clears the persisted state.
    graph.delete_thread("conv-1")
    assert saver.get({"configurable": {"thread_id": "conv-1"}}) is None

