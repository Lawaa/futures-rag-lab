"""Local-first AST Code Review and Safety Guard system.

Combines fast native AST static analysis with optional LLM architectural review.
"""

from __future__ import annotations

from .ast_checker import ASTChecker, ASTIssue, ASTReviewResult, is_test_file_path, summarize_ast
from .git_hook import install_pre_commit_hook
from .hybrid_reviewer import HybridCodeReviewer, HybridReviewReport

__all__ = [
    "ASTChecker",
    "ASTIssue",
    "ASTReviewResult",
    "is_test_file_path",
    "summarize_ast",
    "HybridCodeReviewer",
    "HybridReviewReport",
    "install_pre_commit_hook",
]
