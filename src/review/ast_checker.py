"""Abstract Syntax Tree (AST) static checker and structural condenser.

Performs zero-cost, local-first static analysis for security vulnerabilities
(eval/exec, hardcoded secrets), type annotation coverage, exception hygiene,
and cyclomatic complexity.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class ASTIssue(BaseModel):
    """Static analysis issue detected during AST inspection."""

    category: str = Field(..., description="Issue category: security, type_annotations, exception_handling, complexity")
    severity: str = Field(..., description="Severity level: BLOCKING or WARNING")
    message: str = Field(..., description="Human-readable description of the issue")
    line_number: int = Field(default=1, description="Source code line number (1-indexed)")
    column: int = Field(default=0, description="Column offset (0-indexed)")
    symbol: str | None = Field(default=None, description="Associated function, class, or variable name")


class ASTReviewResult(BaseModel):
    """Aggregated static analysis result for a Python file."""

    file_path: str = Field(..., description="Path to the inspected file")
    passes_safety: bool = Field(default=True, description="False if any BLOCKING security violations exist")
    issues: list[ASTIssue] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)

    @property
    def blocking_issues(self) -> list[ASTIssue]:
        """Return only blocking security/critical issues."""
        return [i for i in self.issues if i.severity == "BLOCKING"]

    @property
    def warnings(self) -> list[ASTIssue]:
        """Return non-blocking style or complexity warnings."""
        return [i for i in self.issues if i.severity == "WARNING"]

    @property
    def has_issues(self) -> bool:
        """Whether any issues or warnings were discovered."""
        return len(self.issues) > 0


_SUSPICIOUS_KEY_PATTERNS = re.compile(
    r"(?:AKIA[0-9A-Z]{16})|(?:ghp_[0-9a-zA-Z]{36})|(?:sk-[a-zA-Z0-9]{32,})|(?:AIza[0-9A-Za-z-_]{35})",
    re.IGNORECASE,
)

_SECRET_VAR_NAMES = {
    "api_key",
    "apikey",
    "secret_key",
    "secret",
    "private_key",
    "access_key",
    "password",
    "auth_token",
    "token",
}

_SAFE_PLACEHOLDERS = {
    "",
    "none",
    "null",
    "test",
    "dummy",
    "default",
    "mock",
    "fake",
    "placeholder",
    "changeme",
    "env",
    "xxx",
    "***",
}

_BRANCH_TYPES = (
    ast.If,
    ast.IfExp,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.ExceptHandler,
    ast.With,
    ast.AsyncWith,
    ast.Assert,
)

_FLOW_MAP = {
    ast.If: "if ...",
    ast.For: "for ...",
    ast.AsyncFor: "for ...",
    ast.While: "while ...",
    ast.Try: "try/except ...",
    ast.Return: "return ...",
    ast.Raise: "raise ...",
}


def is_test_file_path(file_path: str | Path) -> bool:
    """Determine if a file path belongs to test suites, fixtures, or test files."""
    path = Path(file_path)
    parts = [part.lower() for part in path.parts]
    if any(p in {"tests", "test", "testing"} for p in parts):
        return True
    stem = path.stem.lower()
    return stem.startswith("test_") or stem.endswith("_test") or stem == "conftest"


def _calculate_function_complexity(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Calculate cyclomatic complexity for an AST function node."""
    complexity = 1
    for node in ast.walk(func_node):
        if isinstance(node, _BRANCH_TYPES):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            complexity += len(node.values) - 1
        elif hasattr(ast, "match_case") and isinstance(node, getattr(ast, "match_case")):
            if getattr(node, "guard", None) is not None:
                complexity += 1
    return complexity


def _get_flow_tag(node: ast.AST) -> str | None:
    """Map AST node to control flow outline tag."""
    for cls, tag in _FLOW_MAP.items():
        if isinstance(node, cls):
            return tag
    return None


def summarize_ast(tree: ast.AST) -> str:
    """Create a token-condensed structural representation of a Python module AST."""
    lines: list[str] = []

    for node in tree.body:  # type: ignore[attr-defined]
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [alias.name for alias in node.names]
            mod = getattr(node, "module", None)
            prefix = f"from {mod} " if mod else ""
            lines.append(f"{prefix}import {', '.join(names)}")
        elif isinstance(node, ast.ClassDef):
            bases = [ast.unparse(b) for b in node.bases]
            base_str = f"({', '.join(bases)})" if bases else ""
            lines.append(f"\nclass {node.name}{base_str}:")
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    _append_func_summary(item, lines, indent="    ")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            _append_func_summary(node, lines, indent="")

    return "\n".join(lines)


def _append_func_summary(
    func: ast.FunctionDef | ast.AsyncFunctionDef, lines: list[str], indent: str = ""
) -> None:
    async_prefix = "async " if isinstance(func, ast.AsyncFunctionDef) else ""
    ret = f" -> {ast.unparse(func.returns)}" if func.returns else ""

    args = []
    for a in func.args.args:
        ann = f": {ast.unparse(a.annotation)}" if a.annotation else ""
        args.append(f"{a.arg}{ann}")
    arg_str = ", ".join(args)

    lines.append(f"{indent}{async_prefix}def {func.name}({arg_str}){ret}:")

    # Outline internal control flow branches concisely
    branches = [tag for sub in func.body if (tag := _get_flow_tag(sub)) is not None]
    if branches:
        lines.append(f"{indent}    # flow: {', '.join(branches[:6])}")
    else:
        lines.append(f"{indent}    pass")


class ASTChecker:
    """Local-first Python AST code checker and security gate."""

    def __init__(self, complexity_threshold: int = 10) -> None:
        self.complexity_threshold = complexity_threshold

    def _check_call_security(self, node: ast.Call) -> ASTIssue | None:
        """Flag eval() and exec() function invocations."""
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
            return ASTIssue(
                category="security",
                severity="BLOCKING",
                message=f"Dangerous function '{node.func.id}()' is strictly prohibited.",
                line_number=node.lineno,
                column=node.col_offset,
                symbol=node.func.id,
            )
        return None

    def _classify_secret_literal(self, target_name: str, raw_str: str) -> str | None:
        """Classify if literal is BLOCKING token or WARNING secret assignment."""
        if _SUSPICIOUS_KEY_PATTERNS.search(raw_str):
            return "BLOCKING"
        lowered = raw_str.lower()
        if (
            any(w in target_name for w in _SECRET_VAR_NAMES)
            and len(raw_str) >= 12
            and lowered not in _SAFE_PLACEHOLDERS
        ):
            return "WARNING"
        return None

    def _check_assignment_secret(
        self, node: ast.Assign | ast.AnnAssign, is_test_file: bool
    ) -> list[ASTIssue]:
        """Inspect string assignments for unmasked credentials.

        Credential rules are bypassed for test files to avoid false positives
        on mock API keys, test tokens, and fixtures.
        """
        if is_test_file:
            return []

        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        value = node.value
        if not (isinstance(value, ast.Constant) and isinstance(value.value, str)):
            return []

        raw_str = value.value.strip()
        issues: list[ASTIssue] = []

        for target in targets:
            name = target.id.lower() if isinstance(target, ast.Name) else getattr(target, "attr", "").lower()
            severity = self._classify_secret_literal(name, raw_str)
            if severity == "BLOCKING":
                issues.append(
                    ASTIssue(
                        category="security",
                        severity="BLOCKING",
                        message=f"Potential hardcoded secret or API key detected in '{name}'.",
                        line_number=value.lineno,
                        column=value.col_offset,
                        symbol=name,
                    )
                )
            elif severity == "WARNING":
                issues.append(
                    ASTIssue(
                        category="security",
                        severity="WARNING",
                        message=f"Suspicious hardcoded credential literal assigned to '{name}'.",
                        line_number=value.lineno,
                        column=value.col_offset,
                        symbol=name,
                    )
                )
        return issues

    def _check_function_types(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> list[ASTIssue]:
        """Check function arguments and return type annotations."""
        issues: list[ASTIssue] = []
        for arg in node.args.args:
            if arg.arg not in {"self", "cls"} and arg.annotation is None:
                issues.append(
                    ASTIssue(
                        category="type_annotations",
                        severity="WARNING",
                        message=f"Argument '{arg.arg}' in function '{node.name}' is missing type annotation.",
                        line_number=arg.lineno,
                        column=arg.col_offset,
                        symbol=node.name,
                    )
                )
        if node.returns is None and node.name != "__init__":
            issues.append(
                ASTIssue(
                    category="type_annotations",
                    severity="WARNING",
                    message=f"Function '{node.name}' is missing return type annotation.",
                    line_number=node.lineno,
                    column=node.col_offset,
                    symbol=node.name,
                )
            )
        return issues

    def _check_exception_handler(self, node: ast.ExceptHandler) -> ASTIssue | None:
        """Inspect exception handlers for bare except or silent suppression."""
        if node.type is None:
            return ASTIssue(
                category="exception_handling",
                severity="WARNING",
                message="Bare 'except:' clause caught. Specify explicit exception types.",
                line_number=node.lineno,
                column=node.col_offset,
            )
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            return ASTIssue(
                category="exception_handling",
                severity="WARNING",
                message="Silent exception suppression ('except ...: pass') detected.",
                line_number=node.lineno,
                column=node.col_offset,
            )
        return None

    def _check_function_node(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        is_test_file: bool,
        metrics: dict[str, Any],
    ) -> list[ASTIssue]:
        """Check types and complexity on a function node."""
        issues: list[ASTIssue] = []
        if not is_test_file:
            issues.extend(self._check_function_types(node))
        complexity = _calculate_function_complexity(node)
        metrics["complexity"][node.name] = complexity
        if complexity > self.complexity_threshold:
            issues.append(
                ASTIssue(
                    category="complexity",
                    severity="WARNING",
                    message=(
                        f"Function '{node.name}' has high cyclomatic complexity of {complexity} "
                        f"(threshold: {self.complexity_threshold}). Consider refactoring."
                    ),
                    line_number=node.lineno,
                    column=node.col_offset,
                    symbol=node.name,
                )
            )
        return issues

    def _inspect_ast_node(
        self, node: ast.AST, is_test_file: bool, metrics: dict[str, Any]
    ) -> list[ASTIssue]:
        """Dispatch node to appropriate checker."""
        if isinstance(node, ast.Call):
            issue = self._check_call_security(node)
            return [issue] if issue else []
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            return self._check_assignment_secret(node, is_test_file)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return self._check_function_node(node, is_test_file, metrics)
        if isinstance(node, ast.ExceptHandler):
            issue = self._check_exception_handler(node)
            return [issue] if issue else []
        return []

    def check_code(self, code: str, file_path: str = "<string>") -> ASTReviewResult:
        """Parse and inspect Python code string."""
        issues: list[ASTIssue] = []
        metrics: dict[str, Any] = {"complexity": {}}

        try:
            tree = ast.parse(code, filename=file_path)
        except SyntaxError as err:
            issues.append(
                ASTIssue(
                    category="security",
                    severity="BLOCKING",
                    message=f"Syntax error: {err.msg}",
                    line_number=err.lineno or 1,
                    column=err.offset or 0,
                )
            )
            return ASTReviewResult(file_path=file_path, passes_safety=False, issues=issues)

        is_test_file = is_test_file_path(file_path)

        for node in ast.walk(tree):
            issues.extend(self._inspect_ast_node(node, is_test_file, metrics))

        passes_safety = not any(issue.severity == "BLOCKING" for issue in issues)
        return ASTReviewResult(
            file_path=file_path,
            passes_safety=passes_safety,
            issues=issues,
            metrics=metrics,
        )

    def check_file(self, file_path: str | Path) -> ASTReviewResult:
        """Inspect a Python source file from filesystem."""
        path = Path(file_path)
        if not path.exists():
            return ASTReviewResult(
                file_path=str(path),
                passes_safety=False,
                issues=[ASTIssue(category="security", severity="BLOCKING", message=f"File not found: {path}")],
            )
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as err:
            return ASTReviewResult(
                file_path=str(path),
                passes_safety=False,
                issues=[ASTIssue(category="security", severity="BLOCKING", message=f"Failed to read file: {err}")],
            )
        return self.check_code(content, file_path=str(path))
