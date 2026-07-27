"""High-level Retrieval-Augmented Generation orchestration.

:class:`RagService` ties together the retriever, language model and prompt
templates behind a small, testable interface. The retrieval stage — cross-lingual
query preparation, document grading and the self-correction rewrite loop — runs
through a compiled LangGraph pipeline (see :mod:`src.graph`). Generation is kept
separate so sources can be shown before the answer is streamed, and so a turn
never triggers a second retrieval pass.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.vectorstores import VectorStoreRetriever

from .conversation_store import ConversationStore
from .graph import STAGE_LABELS, RetrievalGraph
from .models import Answer, RetrievalResult
from .profiles import ProfileRegistry, load_profiles
from .prompts import (
    get_groundedness_prompt,
    get_qa_prompt,
    is_affirmative,
    is_outside_knowledge,
    outside_knowledge_note,
)
from .settings import Settings

if TYPE_CHECKING:
    from langgraph.checkpoint.base import BaseCheckpointSaver

DEFAULT_SESSION_ID = "default_session"


def _format_context(documents: list[Document]) -> str:
    return "\n\n".join(document.page_content for document in documents)


class RagService:
    """Stateful conversational RAG assistant."""

    def __init__(
        self,
        llm: BaseChatModel,
        retriever: VectorStoreRetriever,
        settings: Settings,
        store: ConversationStore | None = None,
        checkpointer: "BaseCheckpointSaver | None" = None,
    ) -> None:
        self._llm = llm
        self._retriever = retriever
        self._settings = settings
        self._store = store
        self._histories: dict[str, InMemoryChatMessageHistory] = {}
        self._profiles: ProfileRegistry = load_profiles(settings)
        self._retrieval_graph = RetrievalGraph(
            llm, retriever, settings, self._profiles, checkpointer
        )
        self._groundedness_check = settings.enable_groundedness_check
        self._groundedness_chain = (
            get_groundedness_prompt() | llm | StrOutputParser()
        )
        # Answer chains are built per profile (each has its own system prompt)
        # and cached, since routing can select a different profile per turn.
        self._answer_chains: dict[str, object] = {}

    def _answer_chain(self, profile_id: str | None):
        """Return the cached answer chain for a profile (built on first use)."""
        profile = self._profiles.get(profile_id)
        chain = self._answer_chains.get(profile.id)
        if chain is None:
            prompt = get_qa_prompt(self._settings.language, profile.system_prompt)
            chain = prompt | self._llm | StrOutputParser()
            self._answer_chains[profile.id] = chain
        return chain

    # -- history --------------------------------------------------------------
    def _history(self, session_id: str) -> InMemoryChatMessageHistory:
        history = self._histories.get(session_id)
        if history is not None:
            return history

        history = InMemoryChatMessageHistory()
        if self._store is not None:
            for role, content in self._store.load_messages(session_id):
                if role == "human":
                    history.add_user_message(content)
                else:
                    history.add_ai_message(content)
        self._histories[session_id] = history
        return history

    def reset_history(self, session_id: str = DEFAULT_SESSION_ID) -> None:
        """Clear a conversation's history from memory and persistent storage."""
        self._histories.pop(session_id, None)
        self._retrieval_graph.delete_thread(session_id)
        if self._store is not None:
            self._store.delete_conversation(session_id)

    # -- persisted conversations ---------------------------------------------
    def list_conversations(self, limit: int = 15) -> list[dict[str, str]]:
        """Return recent persisted conversations (most recent first)."""
        if self._store is None:
            return []
        return self._store.list_conversations(limit)

    def get_messages(self, session_id: str) -> list[tuple[str, str]]:
        """Return the ordered ``(role, content)`` pairs for a conversation."""
        if self._store is not None:
            return self._store.load_messages(session_id)
        return [
            ("human" if message.type == "human" else "ai", message.content)
            for message in self._history(session_id).messages
        ]

    def delete_conversation(self, session_id: str) -> None:
        """Delete a conversation entirely (alias of :meth:`reset_history`)."""
        self.reset_history(session_id)

    def rename_conversation(self, session_id: str, title: str) -> str | None:
        """Rename a persisted conversation, returning the stored title or ``None``."""
        if self._store is None:
            return None
        return self._store.rename_conversation(session_id, title)

    def set_pinned(self, session_id: str, pinned: bool) -> bool:
        """Pin/unpin a conversation so it survives automatic pruning."""
        if self._store is None:
            return False
        return self._store.set_pinned(session_id, pinned)

    # -- retrieval ------------------------------------------------------------
    def retrieve(
        self, question: str, session_id: str = DEFAULT_SESSION_ID
    ) -> RetrievalResult:
        """Run the LangGraph retrieval pipeline for a question.

        The graph prepares a cross-lingual standalone query, retrieves documents
        and — when self-correction is enabled — grades them and rewrites the query
        until relevant results are found or the retry budget is exhausted.
        """
        history = self._history(session_id)
        state = self._retrieval_graph.run(question, history.messages, session_id)
        return RetrievalResult(
            standalone_question=state.get("search_query", question),
            documents=state.get("documents", []),
            retry_count=state.get("retry_count", 0),
            profile_id=state.get("profile_id") or self._profiles.active_id,
        )

    # -- generation -----------------------------------------------------------
    def _answer_inputs(
        self, question: str, retrieval: RetrievalResult, session_id: str
    ) -> dict:
        return {
            "question": question,
            "context": _format_context(retrieval.documents),
            "chat_history": self._history(session_id).messages,
        }

    def _remember(self, session_id: str, question: str, answer: str) -> None:
        history = self._history(session_id)
        history.add_user_message(question)
        history.add_ai_message(answer)
        if self._store is not None:
            self._store.append_turn(session_id, question, answer)

    # -- groundedness (Self-RAG / CRAG) --------------------------------------
    def _is_grounded(self, retrieval: RetrievalResult, text: str) -> bool:
        """Whether the answer is supported by the retrieved documents.

        The model is instructed to prepend a disclaimer when it falls back to
        general knowledge, which is a free, deterministic signal. When enabled,
        an extra Self-RAG check verifies answers that carry no disclaimer, to
        catch silent hallucinations.
        """
        if not retrieval.documents:
            return False
        if is_outside_knowledge(text):
            return False
        if not self._groundedness_check:
            return True
        verdict = self._groundedness_chain.invoke(
            {"context": _format_context(retrieval.documents), "answer": text}
        )
        return is_affirmative(verdict)

    def _finalize(
        self, retrieval: RetrievalResult, text: str
    ) -> tuple[str, list, bool]:
        """Apply groundedness: label ungrounded answers and drop false sources."""
        if self._is_grounded(retrieval, text):
            return text, retrieval.sources, True
        if not is_outside_knowledge(text):
            note = outside_knowledge_note(self._settings.language)
            text = f"{note}\n\n{text}"
        return text, [], False

    def answer(
        self, question: str, session_id: str = DEFAULT_SESSION_ID
    ) -> Answer:
        """Generate a complete answer with its supporting sources."""
        retrieval = self.retrieve(question, session_id)
        raw = self._answer_chain(retrieval.profile_id).invoke(
            self._answer_inputs(question, retrieval, session_id)
        )
        text, sources, grounded = self._finalize(retrieval, raw)
        self._remember(session_id, question, text)
        return Answer(text=text, sources=sources, grounded=grounded)

    def stream_answer(
        self,
        question: str,
        retrieval: RetrievalResult,
        session_id: str = DEFAULT_SESSION_ID,
    ) -> Iterator[str]:
        """Stream answer tokens for a pre-computed retrieval, persisting history.

        Accepting the :class:`RetrievalResult` lets callers display sources
        before generation begins without retrieving twice.
        """
        chunks: list[str] = []
        for token in self._answer_chain(retrieval.profile_id).stream(
            self._answer_inputs(question, retrieval, session_id)
        ):
            chunks.append(token)
            yield token
        self._remember(session_id, question, "".join(chunks))

    def stream_events(
        self, question: str, session_id: str = DEFAULT_SESSION_ID
    ) -> Iterator[dict]:
        """Stream the full turn as structured events for a live progress UI.

        Emits ``status`` events as each retrieval stage completes, ``token``
        events while the answer is generated, and a terminal ``done`` event
        carrying the sources, groundedness verdict and any hallucination note.
        """
        history = self._history(session_id)
        final_state: dict = {}
        for node_name, node_state in self._retrieval_graph.stream(
            question, history.messages, session_id
        ):
            final_state.update(node_state)
            stage = STAGE_LABELS.get(node_name)
            if stage is not None:
                yield {"type": "status", "stage": stage}

        retrieval = RetrievalResult(
            standalone_question=final_state.get("search_query", question),
            documents=final_state.get("documents", []),
            retry_count=final_state.get("retry_count", 0),
            profile_id=final_state.get("profile_id") or self._profiles.active_id,
        )

        yield {"type": "status", "stage": "answering"}
        chunks: list[str] = []
        for token in self._answer_chain(retrieval.profile_id).stream(
            self._answer_inputs(question, retrieval, session_id)
        ):
            chunks.append(token)
            yield {"type": "token", "text": token}
        raw = "".join(chunks)

        text, sources, grounded = self._finalize(retrieval, raw)
        # When _finalize prepends an "outside knowledge" note to a silent
        # hallucination, surface just that note so the UI can show it above the
        # already-streamed answer body.
        note = None
        if not grounded and text.endswith(raw) and len(text) > len(raw):
            note = text[: len(text) - len(raw)].strip()

        self._remember(session_id, question, text)
        yield {
            "type": "done",
            "grounded": grounded,
            "sources": [{"name": s.name, "page": s.page} for s in sources],
            "note": note,
        }
