"""Hybrid Code Reviewer combining fast local AST analysis and LLM architectural feedback.

Runs AST checks first to enforce strict security boundaries (eval/exec, hardcoded secrets).
If safe, condenses the AST structure and queries the configured LLM for high-value
architectural and maintainability review.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Sequence

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field

from ..credentials import get_stored_api_key
from ..llm import build_llm
from ..logging_config import get_logger
from ..prompts import get_code_review_prompt
from ..settings import Settings, get_settings
from .ast_checker import ASTChecker, ASTReviewResult, summarize_ast

logger = get_logger(__name__)


class HybridReviewReport(BaseModel):
    """Combined report of AST static analysis and LLM architectural review."""

    file_path: str
    passes_safety: bool
    ast_result: ASTReviewResult
    ast_summary: str | None = None
    llm_feedback: str | None = None
    llm_called: bool = False
    verdict: str = Field(default="PASS", description="PASS, WARNINGS, or BLOCKED")


def _extract_text_content(content: Any) -> str:
    """Extract plain string from LangChain response content."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            elif hasattr(item, "text"):
                parts.append(str(item.text))
            else:
                parts.append(str(item))
        return "\n".join(parts).strip()
    return str(content).strip()


class HybridCodeReviewer:
    """Orchestrates two-stage local code review: AST Gate -> LLM Review."""

    def __init__(
        self,
        settings: Settings | None = None,
        llm: BaseChatModel | None = None,
        complexity_threshold: int = 10,
    ) -> None:
        self.settings = settings or get_settings()
        self._llm = llm
        self.ast_checker = ASTChecker(complexity_threshold=complexity_threshold)

    @property
    def llm(self) -> BaseChatModel:
        """Lazily initialize chat model."""
        if self._llm is None:
            api_key = get_stored_api_key() if self.settings.uses_gemini else None
            self._llm = build_llm(self.settings, api_key=api_key)
        return self._llm

    def _call_llm_review(
        self, path: Path, ast_result: ASTReviewResult, ast_summary: str
    ) -> tuple[str, bool]:
        """Invoke LLM with condensed AST summary and static warnings."""
        issues_text = "\n".join(
            f"- [{i.category.upper()}] Line {i.line_number}: {i.message}"
            for i in ast_result.issues
        ) or "None. All static AST checks passed."

        prompt_messages = get_code_review_prompt().format_messages(
            file_path=str(path),
            issues=issues_text,
            ast_summary=ast_summary,
        )

        try:
            logger.info("Requesting LLM architectural review for '%s'...", path)
            response = self.llm.invoke(prompt_messages)
            return _extract_text_content(response.content), True
        except Exception as err:
            logger.warning("LLM code review call failed: %s", err)
            return f"(LLM Review unavailable: {err})", True

    def review_file(
        self,
        file_path: str | Path,
        enable_llm_review: bool = False,
    ) -> HybridReviewReport:
        """Execute hybrid review on a single Python file."""
        path = Path(file_path)
        ast_result = self.ast_checker.check_file(path)

        # Stage 1: Security Short-Circuit
        if not ast_result.passes_safety:
            logger.warning("Security violations detected in '%s'. Aborting LLM review.", path)
            return HybridReviewReport(
                file_path=str(path),
                passes_safety=False,
                ast_result=ast_result,
                llm_called=False,
                verdict="BLOCKED",
            )

        # Stage 2: Structural AST condensation
        ast_summary = None
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            ast_summary = summarize_ast(tree)
        except Exception as err:
            logger.debug("Failed to build condensed AST summary: %s", err)

        verdict = "WARNINGS" if ast_result.has_issues else "PASS"

        if not enable_llm_review or not ast_summary:
            return HybridReviewReport(
                file_path=str(path),
                passes_safety=True,
                ast_result=ast_result,
                ast_summary=ast_summary,
                llm_called=False,
                verdict=verdict,
            )

        # Stage 3: LLM Architectural Feedback
        feedback, called = self._call_llm_review(path, ast_result, ast_summary)
        return HybridReviewReport(
            file_path=str(path),
            passes_safety=True,
            ast_result=ast_result,
            ast_summary=ast_summary,
            llm_feedback=feedback,
            llm_called=called,
            verdict=verdict,
        )

    def review_files(
        self,
        file_paths: Sequence[str | Path],
        enable_llm_review: bool = False,
    ) -> list[HybridReviewReport]:
        """Review multiple Python files sequentially."""
        return [self.review_file(p, enable_llm_review=enable_llm_review) for p in file_paths]
