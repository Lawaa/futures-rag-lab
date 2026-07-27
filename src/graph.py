"""LangGraph orchestration for the retrieval stage of the RAG pipeline.

This graph is the control-flow engine behind :class:`~src.rag_service.RagService`.
It turns a raw user turn into a grounded set of documents using three ideas:

* **Cross-lingual search** – the ``prepare_query`` node always rewrites the user's
  question into a standalone query in the corpus language (``retrieval_language``),
  so a Hungarian question can still match English documents (and vice-versa).
* **Self-correction loop** – retrieved documents are graded for relevance; when
  they are not good enough the ``rewrite_query`` node reformulates the search and
  the graph loops back to ``retrieve`` (bounded by ``max_retrieval_retries``).
* **Single pass per turn** – generation is intentionally *not* part of this graph
  so the service can show sources first and stream the answer without paying for
  a second retrieval pass, keeping the number of LLM calls (and rate-limit
  pressure) to a minimum.
"""

from __future__ import annotations

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, TypedDict

from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.vectorstores import VectorStoreRetriever
from langgraph.graph import END, START, StateGraph

from .logging_config import get_logger
from .profiles import ProfileRegistry
from .prompts import (
    get_grade_prompt,
    get_multi_query_prompt,
    get_rewrite_prompt,
    get_router_prompt,
    get_search_query_prompt,
    language_name,
)
from .settings import Settings

if TYPE_CHECKING:
    from langgraph.checkpoint.base import BaseCheckpointSaver

logger = get_logger(__name__)

# Default thread used when no conversation id is supplied (checkpointing).
DEFAULT_THREAD_ID = "default_session"

# Tokens that count as an affirmative relevance grade across languages.
_POSITIVE_GRADES = ("yes", "true", "relevant", "igen")

# Reciprocal Rank Fusion damping constant (higher = flatter rank weighting).
_RRF_K = 60

# Human-facing pipeline stage for each graph node, streamed to the UI so users
# can watch retrieval progress (routing -> preparing -> ... -> answering).
STAGE_LABELS: dict[str, str] = {
    "route": "routing",
    "prepare_query": "preparing",
    "expand": "expanding",
    "retrieve": "retrieving",
    "grade": "grading",
    "rewrite": "rewriting",
}


class RetrievalState(TypedDict, total=False):
    """Mutable state threaded through the retrieval graph."""

    question: str
    chat_history: list[BaseMessage]
    search_query: str
    search_queries: list[str]
    documents: list[Document]
    relevant: bool
    retry_count: int
    profile_id: str


def _clean_query(text: str) -> str:
    """Strip whitespace and surrounding quotes the model may add to a query."""
    return text.strip().strip('"').strip("'").strip()


def _format_context(documents: list[Document]) -> str:
    return "\n\n".join(document.page_content for document in documents)


def _doc_key(document: Document) -> tuple:
    """A stable identity for a document so fused lists can be de-duplicated."""
    meta = document.metadata or {}
    return (meta.get("source"), meta.get("page"), document.page_content)


def _reciprocal_rank_fusion(
    ranked_lists: list[list[Document]], top_k: int
) -> list[Document]:
    """Fuse several ranked document lists into one via Reciprocal Rank Fusion.

    RRF rewards documents that rank highly across multiple query variants without
    needing calibrated scores, making it a robust, dependency-free reranker for
    multi-query fan-out.
    """
    scores: dict[tuple, float] = {}
    representatives: dict[tuple, Document] = {}
    for documents in ranked_lists:
        for rank, document in enumerate(documents):
            key = _doc_key(document)
            scores[key] = scores.get(key, 0.0) + 1.0 / (_RRF_K + rank + 1)
            representatives.setdefault(key, document)
    ordered = sorted(scores, key=lambda key: scores[key], reverse=True)
    return [representatives[key] for key in ordered[:top_k]]


class RetrievalGraph:
    """Compiled LangGraph pipeline that produces relevant documents for a turn."""

    def __init__(
        self,
        llm: BaseChatModel,
        retriever: VectorStoreRetriever,
        settings: Settings,
        profiles: ProfileRegistry | None = None,
        checkpointer: "BaseCheckpointSaver | None" = None,
    ) -> None:
        self._retriever = retriever
        self._max_retries = max(0, settings.max_retrieval_retries)
        self._self_correct = settings.enable_self_correction
        self._profiles = profiles
        self._checkpointer = checkpointer
        self._multi_query = settings.enable_multi_query
        self._top_k = settings.retriever_k
        self._route_enabled = bool(
            settings.enable_profile_routing
            and profiles is not None
            and profiles.routable
        )
        target_language = language_name(settings.retrieval_language)

        self._search_chain = (
            get_search_query_prompt(target_language) | llm | StrOutputParser()
        )
        self._grade_chain = get_grade_prompt() | llm | StrOutputParser()
        self._rewrite_chain = (
            get_rewrite_prompt(target_language) | llm | StrOutputParser()
        )
        self._router_chain = (
            get_router_prompt() | llm | StrOutputParser()
            if self._route_enabled
            else None
        )
        self._multi_query_chain = (
            get_multi_query_prompt(target_language, settings.multi_query_count)
            | llm
            | StrOutputParser()
            if self._multi_query
            else None
        )
        self._graph = self._build()

    def _entry_after_query(self) -> str:
        """Node reached after a (re)written query: fan-out first if enabled."""
        return "expand" if self._multi_query else "retrieve"

    # -- nodes ----------------------------------------------------------------
    def _route_profile(self, state: RetrievalState) -> dict:
        """Classify the question and select the best-matching business profile."""
        assert self._profiles is not None and self._router_chain is not None
        choice = self._router_chain.invoke(
            {
                "question": state["question"],
                "chat_history": state.get("chat_history") or [],
                "profiles": self._profiles.listing(),
            }
        )
        profile = self._profiles.get(_clean_query(choice))
        logger.info("Routed question to profile '%s'.", profile.id)
        return {"profile_id": profile.id}

    def _prepare_query(self, state: RetrievalState) -> dict:
        """Resolve references and translate the question into the corpus language."""
        question = state["question"]
        history = state.get("chat_history") or []
        query = self._search_chain.invoke(
            {"question": question, "chat_history": history}
        )
        return {"search_query": _clean_query(query) or question, "retry_count": 0}

    def _expand_queries(self, state: RetrievalState) -> dict:
        """Fan the prepared query out into several complementary variants."""
        assert self._multi_query_chain is not None
        query = state["search_query"]
        raw = self._multi_query_chain.invoke({"query": query})
        variants = [_clean_query(line) for line in raw.splitlines()]
        # Keep the original query first, drop blanks and duplicates.
        queries = list(dict.fromkeys([query, *(v for v in variants if v)]))
        logger.info("Expanded search into %d query variants.", len(queries))
        return {"search_queries": queries}

    def _retrieve(self, state: RetrievalState) -> dict:
        """Fetch candidate documents for the current query (or fused variants)."""
        queries = state.get("search_queries") if self._multi_query else None
        if queries:
            with ThreadPoolExecutor(max_workers=min(len(queries), 8)) as executor:
                ranked_lists = list(executor.map(self._retriever.invoke, queries))
            documents = _reciprocal_rank_fusion(ranked_lists, self._top_k)
            return {"documents": documents}
        documents = self._retriever.invoke(state["search_query"])
        return {"documents": documents}

    def _grade(self, state: RetrievalState) -> dict:
        """Judge whether the retrieved documents can support an answer."""
        documents = state.get("documents") or []
        if not documents:
            return {"relevant": False}
        verdict = self._grade_chain.invoke(
            {"question": state["question"], "context": _format_context(documents)}
        )
        relevant = any(token in verdict.lower() for token in _POSITIVE_GRADES)
        return {"relevant": relevant}

    def _rewrite_query(self, state: RetrievalState) -> dict:
        """Reformulate a failed search query and count the retry."""
        rewritten = self._rewrite_chain.invoke(
            {"question": state["question"], "query": state["search_query"]}
        )
        retry_count = state.get("retry_count", 0) + 1
        logger.info("Rewriting search query (attempt %d).", retry_count)
        return {
            "search_query": _clean_query(rewritten) or state["search_query"],
            "retry_count": retry_count,
        }

    # -- routing --------------------------------------------------------------
    def _route_after_grade(self, state: RetrievalState) -> str:
        """Accept the documents, or rewrite the query while retries remain."""
        if state.get("relevant"):
            return "accept"
        if state.get("retry_count", 0) < self._max_retries:
            return "rewrite"
        logger.info("Retry budget exhausted; answering with best-effort documents.")
        return "accept"

    # -- assembly -------------------------------------------------------------
    def _build(self):
        builder = StateGraph(RetrievalState)
        builder.add_node("prepare_query", self._prepare_query)
        builder.add_node("retrieve", self._retrieve)

        if self._route_enabled:
            builder.add_node("route", self._route_profile)
            builder.add_edge(START, "route")
            builder.add_edge("route", "prepare_query")
        else:
            builder.add_edge(START, "prepare_query")

        retrieve_entry = self._entry_after_query()
        if self._multi_query:
            builder.add_node("expand", self._expand_queries)
            builder.add_edge("prepare_query", "expand")
            builder.add_edge("expand", "retrieve")
        else:
            builder.add_edge("prepare_query", "retrieve")

        if self._self_correct:
            builder.add_node("grade", self._grade)
            builder.add_node("rewrite", self._rewrite_query)
            builder.add_edge("retrieve", "grade")
            builder.add_conditional_edges(
                "grade",
                self._route_after_grade,
                {"accept": END, "rewrite": "rewrite"},
            )
            builder.add_edge("rewrite", retrieve_entry)
        else:
            builder.add_edge("retrieve", END)

        return builder.compile(checkpointer=self._checkpointer)

    def _config(self, session_id: str) -> dict | None:
        """Per-conversation runtime config that keys the checkpointer thread."""
        if self._checkpointer is None:
            return None
        return {"configurable": {"thread_id": session_id or DEFAULT_THREAD_ID}}

    # -- public API -----------------------------------------------------------
    def run(
        self,
        question: str,
        chat_history: list[BaseMessage] | None = None,
        session_id: str = DEFAULT_THREAD_ID,
    ) -> RetrievalState:
        """Execute the graph and return the final state for a single turn."""
        return self._graph.invoke(
            {"question": question, "chat_history": chat_history or []},
            config=self._config(session_id),
        )

    def stream(
        self,
        question: str,
        chat_history: list[BaseMessage] | None = None,
        session_id: str = DEFAULT_THREAD_ID,
    ) -> Iterator[tuple[str, RetrievalState]]:
        """Yield ``(node_name, state_update)`` pairs as each stage completes."""
        inputs = {"question": question, "chat_history": chat_history or []}
        for update in self._graph.stream(
            inputs, config=self._config(session_id), stream_mode="updates"
        ):
            for node_name, node_state in update.items():
                yield node_name, node_state or {}

    def delete_thread(self, session_id: str) -> None:
        """Discard the persisted checkpoint for a conversation, if any."""
        if self._checkpointer is None:
            return
        try:
            self._checkpointer.delete_thread(session_id or DEFAULT_THREAD_ID)
        except Exception:  # pragma: no cover - best-effort cleanup
            logger.debug("Could not delete checkpoint thread '%s'.", session_id)

