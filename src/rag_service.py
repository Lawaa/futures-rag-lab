"""High-level Retrieval-Augmented Generation orchestration.

:class:`RagService` ties together the retriever, language model and prompt
templates behind a small, testable interface. It performs query rephrasing and
retrieval exactly once per turn, then exposes both streaming and non-streaming
answer generation so the CLI and API can share the same logic.
"""

from __future__ import annotations

from collections.abc import Iterator

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.vectorstores import VectorStoreRetriever

from .models import Answer, RetrievalResult
from .prompts import CONTEXTUALIZE_PROMPT, QA_PROMPT
from .settings import Settings

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
    ) -> None:
        self._llm = llm
        self._retriever = retriever
        self._settings = settings
        self._histories: dict[str, InMemoryChatMessageHistory] = {}
        self._rephrase_chain = CONTEXTUALIZE_PROMPT | llm | StrOutputParser()
        self._answer_chain = QA_PROMPT | llm | StrOutputParser()

    # -- history --------------------------------------------------------------
    def _history(self, session_id: str) -> InMemoryChatMessageHistory:
        return self._histories.setdefault(session_id, InMemoryChatMessageHistory())

    def reset_history(self, session_id: str = DEFAULT_SESSION_ID) -> None:
        """Clear the conversation history for a session."""
        self._histories.pop(session_id, None)

    # -- retrieval ------------------------------------------------------------
    def _standalone_question(self, question: str, session_id: str) -> str:
        """Rephrase a follow-up into a standalone query using chat history."""
        history = self._history(session_id)
        if not history.messages:
            return question
        return self._rephrase_chain.invoke(
            {"question": question, "chat_history": history.messages}
        )

    def retrieve(
        self, question: str, session_id: str = DEFAULT_SESSION_ID
    ) -> RetrievalResult:
        """Rephrase and retrieve supporting documents for a question."""
        standalone = self._standalone_question(question, session_id)
        documents = self._retriever.invoke(standalone)
        return RetrievalResult(standalone_question=standalone, documents=documents)

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

    def answer(
        self, question: str, session_id: str = DEFAULT_SESSION_ID
    ) -> Answer:
        """Generate a complete answer with its supporting sources."""
        retrieval = self.retrieve(question, session_id)
        text = self._answer_chain.invoke(
            self._answer_inputs(question, retrieval, session_id)
        )
        self._remember(session_id, question, text)
        return Answer(text=text, sources=retrieval.sources)

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
        for token in self._answer_chain.stream(
            self._answer_inputs(question, retrieval, session_id)
        ):
            chunks.append(token)
            yield token
        self._remember(session_id, question, "".join(chunks))