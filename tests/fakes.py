"""Test doubles shared across the suite.

The LangGraph retrieval pipeline issues several LLM calls per turn (query
preparation, grading, optional rewriting) plus a generation call. A plain
message-cycling fake makes those tests brittle, so :class:`RoutingFakeChatModel`
inspects the system prompt of each call and returns a role-appropriate reply.
"""

from __future__ import annotations

from typing import Any

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class RoutingFakeChatModel(BaseChatModel):
    """A deterministic chat model that routes replies by the prompt's role.

    Each response is chosen from the system prompt's marker phrase, so the graph
    can call it any number of times in any order and still get sensible output.
    """

    search_response: str = "translated search query"
    grade_response: str = "yes"
    rewrite_response: str = "rewritten search query"
    answer_response: str = "Fake answer"
    groundedness_response: str = "yes"
    router_response: str = "default"
    multi_query_response: str = "alt query 1\nalt query 2"

    @property
    def _llm_type(self) -> str:
        return "routing-fake"

    def _route(self, messages: list[BaseMessage]) -> str:
        system = messages[0].content.lower() if messages else ""
        if "relevance grader" in system:
            return self.grade_response
        if "groundedness judge" in system:
            return self.groundedness_response
        if "query optimization expert" in system:
            return self.rewrite_response
        if "query preparation assistant" in system:
            return self.search_response
        if "query expansion assistant" in system:
            return self.multi_query_response
        if "routing assistant" in system:
            return self.router_response
        return self.answer_response

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        message = AIMessage(content=self._route(messages))
        return ChatResult(generations=[ChatGeneration(message=message)])
