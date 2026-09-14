"""Unit tests for the AST Code Review and Safety Guard system.

Verifies detection of eval/exec, hardcoded credentials, missing type hints,
broad exception handling, cyclomatic complexity, hybrid reviewer workflow,
and git hook installer.
"""

from __future__ import annotations

import ast
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage

from src.review.ast_checker import (
    ASTChecker,
    _calculate_function_complexity,
    is_test_file_path,
    summarize_ast,
)
from src.review.cli import build_arg_parser, discover_python_files
from src.review.git_hook import install_pre_commit_hook
from src.review.hybrid_reviewer import HybridCodeReviewer
from src.settings import Settings


# --------------------------------------------------------------------------- #
# Security Guard Tests (eval, exec, secrets)
# --------------------------------------------------------------------------- #

def test_ast_checker_catches_eval_and_exec() -> None:
    code = """
def run_dynamic(user_input: str) -> None:
    eval(user_input)
    exec("print('hello')")
"""
    checker = ASTChecker()
    result = checker.check_code(code)

    assert result.passes_safety is False
    assert len(result.blocking_issues) == 2
    assert any("eval()" in issue.message for issue in result.blocking_issues)
    assert any("exec()" in issue.message for issue in result.blocking_issues)


def test_ast_checker_catches_hardcoded_api_key_pattern() -> None:
    code = 'AWS_KEY = "AKIA1234567890ABCDEF"'
    checker = ASTChecker()
    result = checker.check_code(code)

    assert result.passes_safety is False
    assert len(result.blocking_issues) == 1
    assert "hardcoded secret" in result.blocking_issues[0].message.lower()


def test_ast_checker_warns_on_suspicious_secret_assignment() -> None:
    code = """
api_key = "super_confidential_token_value_here"
safe_val = "test"
"""
    checker = ASTChecker()
    result = checker.check_code(code)

    # Suspicious literal warning (non-blocking)
    assert result.passes_safety is True
    warnings = [w for w in result.warnings if w.category == "security"]
    assert len(warnings) == 1
    assert "api_key" in warnings[0].message


# --------------------------------------------------------------------------- #
# Type Annotation Tests
# --------------------------------------------------------------------------- #

def test_ast_checker_detects_missing_type_hints() -> None:
    code = """
def unannotated_func(x, y: int):
    return x + y

class Demo:
    def method(self, val):
        pass
"""
    checker = ASTChecker()
    result = checker.check_code(code)

    type_issues = [i for i in result.issues if i.category == "type_annotations"]
    # 1: arg x missing annotation
    # 2: unannotated_func missing return annotation
    # 3: val in Demo.method missing annotation
    # 4: Demo.method missing return annotation
    assert len(type_issues) >= 3
    messages = " ".join(i.message for i in type_issues)
    assert "Argument 'x'" in messages
    assert "missing return type" in messages


def test_ast_checker_passes_fully_annotated_function() -> None:
    code = """
def add(a: int, b: int) -> int:
    return a + b

class Math:
    def __init__(self, value: int) -> None:
        self.value = value

    def compute(self, factor: float) -> float:
        return self.value * factor
"""
    checker = ASTChecker()
    result = checker.check_code(code)
    type_issues = [i for i in result.issues if i.category == "type_annotations"]
    assert len(type_issues) == 0


# --------------------------------------------------------------------------- #
# Exception Handling Hygiene Tests
# --------------------------------------------------------------------------- #

def test_ast_checker_detects_bare_except() -> None:
    code = """
def risky_operation() -> None:
    try:
        x = 1 / 0
    except:
        print("error")
"""
    checker = ASTChecker()
    result = checker.check_code(code)
    except_issues = [i for i in result.issues if i.category == "exception_handling"]
    assert len(except_issues) == 1
    assert "Bare 'except:'" in except_issues[0].message


def test_ast_checker_detects_silent_exception_suppression() -> None:
    code = """
def ignore_errors() -> None:
    try:
        x = 1 / 0
    except Exception:
        pass
"""
    checker = ASTChecker()
    result = checker.check_code(code)
    except_issues = [i for i in result.issues if i.category == "exception_handling"]
    assert len(except_issues) == 1
    assert "Silent exception suppression" in except_issues[0].message


# --------------------------------------------------------------------------- #
# Cyclomatic Complexity Tests
# --------------------------------------------------------------------------- #

def test_ast_checker_calculates_cyclomatic_complexity() -> None:
    code = """
def complex_algorithm(x: int, y: int) -> int:
    if x > 0 and y > 0:
        for i in range(x):
            if i % 2 == 0:
                print(i)
            elif i % 3 == 0:
                print(i)
    elif x < 0:
        while y > 0:
            y -= 1
            if y == 5:
                break
    return x + y
"""
    checker = ASTChecker(complexity_threshold=5)
    result = checker.check_code(code)

    complexity_issues = [i for i in result.issues if i.category == "complexity"]
    assert len(complexity_issues) == 1
    assert "high cyclomatic complexity" in complexity_issues[0].message
    assert result.metrics["complexity"]["complex_algorithm"] > 5


def test_calculate_function_complexity_simple() -> None:
    tree = ast.parse("def simple() -> int:\n    return 42")
    func_node = tree.body[0]
    assert isinstance(func_node, ast.FunctionDef)
    assert _calculate_function_complexity(func_node) == 1


# --------------------------------------------------------------------------- #
# AST Summarizer Tests
# --------------------------------------------------------------------------- #

def test_summarize_ast_strips_docstrings_and_condenses() -> None:
    code = '''"""Module docstring that should be omitted."""

from pathlib import Path
import os

class Processor:
    """Class docstring."""
    def run(self, flag: bool) -> None:
        """Method docstring."""
        if flag:
            x = 1
        return None
'''
    tree = ast.parse(code)
    summary = summarize_ast(tree)

    assert "Module docstring" not in summary
    assert "Method docstring" not in summary
    assert "class Processor:" in summary
    assert "def run(self, flag: bool) -> None:" in summary
    assert "if ..." in summary


# --------------------------------------------------------------------------- #
# Hybrid Reviewer Tests
# --------------------------------------------------------------------------- #

def test_hybrid_reviewer_blocks_on_security_violation(tmp_path: Path) -> None:
    bad_file = tmp_path / "unsafe.py"
    bad_file.write_text("def run(cmd: str) -> None:\n    eval(cmd)\n", encoding="utf-8")

    mock_llm = MagicMock()
    reviewer = HybridCodeReviewer(llm=mock_llm)
    report = reviewer.review_file(bad_file, enable_llm_review=True)

    assert report.passes_safety is False
    assert report.verdict == "BLOCKED"
    # Verify LLM was short-circuited and NEVER called
    mock_llm.invoke.assert_not_called()
    assert report.llm_called is False


def test_hybrid_reviewer_calls_llm_on_safe_code(tmp_path: Path) -> None:
    good_file = tmp_path / "safe.py"
    good_file.write_text("def greet(name: str) -> str:\n    return f'Hello {name}'\n", encoding="utf-8")

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="Code architecture is clean and well structured.")

    reviewer = HybridCodeReviewer(llm=mock_llm)
    report = reviewer.review_file(good_file, enable_llm_review=True)

    assert report.passes_safety is True
    assert report.verdict == "PASS"
    assert report.llm_called is True
    assert "clean and well structured" in str(report.llm_feedback)
    mock_llm.invoke.assert_called_once()


# --------------------------------------------------------------------------- #
# Git Hook Installer Tests
# --------------------------------------------------------------------------- #

def test_install_pre_commit_hook(tmp_path: Path) -> None:
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    hook_path = install_pre_commit_hook(repo_root=tmp_path)
    assert hook_path.exists()
    content = hook_path.read_text(encoding="utf-8")
    assert "uv run python -m src.review.cli --staged" in content


def test_install_pre_commit_hook_fails_when_not_git_repo(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        install_pre_commit_hook(repo_root=tmp_path)


# --------------------------------------------------------------------------- #
# CLI Parser & Discovery Tests
# --------------------------------------------------------------------------- #

def test_cli_parser_options() -> None:
    parser = build_arg_parser()
    args = parser.parse_args(["--staged", "--llm-review", "--complexity-threshold", "15"])
    assert args.staged is True
    assert args.llm_review is True
    assert args.complexity_threshold == 15


def test_discover_python_files(tmp_path: Path) -> None:
    sub = tmp_path / "sub"
    sub.mkdir()
    f1 = tmp_path / "a.py"
    f2 = sub / "b.py"
    f3 = tmp_path / "ignore.txt"

    f1.write_text("x = 1")
    f2.write_text("y = 2")
    f3.write_text("data")

    discovered = discover_python_files([str(tmp_path)])
    names = [p.name for p in discovered]
    assert "a.py" in names
    assert "b.py" in names
    assert "ignore.txt" not in names


def test_is_test_file_path() -> None:
    assert is_test_file_path("tests/test_review.py") is True
    assert is_test_file_path("tests/unit/test_foo.py") is True
    assert is_test_file_path("src/module_test.py") is True
    assert is_test_file_path("src/test_something.py") is True
    assert is_test_file_path("conftest.py") is True
    assert is_test_file_path("src/review/ast_checker.py") is False
    assert is_test_file_path("<string>") is False


def test_ast_checker_skips_credential_checks_on_test_files() -> None:
    code = 'AWS_KEY = "AKIA1234567890ABCDEF"'
    checker = ASTChecker()
    # In test files, mock credentials are bypassed to eliminate false positives
    result = checker.check_code(code, file_path="tests/test_credentials.py")
    assert result.passes_safety is True
    assert len(result.blocking_issues) == 0


def test_ast_checker_skips_type_annotation_checks_on_test_files() -> None:
    code = """
def test_something(fixture_arg):
    assert fixture_arg is not None
"""
    checker = ASTChecker()
    result = checker.check_code(code, file_path="tests/test_logic.py")
    assert result.passes_safety is True
    # Missing type annotations in test files do not trigger warnings
    type_warnings = [w for w in result.warnings if w.category == "type_annotations"]
    assert len(type_warnings) == 0


def test_cli_exclude_tests_flag(tmp_path: Path) -> None:
    src_dir = tmp_path / "src"
    tests_dir = tmp_path / "tests"
    src_dir.mkdir()
    tests_dir.mkdir()

    f1 = src_dir / "app.py"
    f2 = tests_dir / "test_app.py"
    f1.write_text("x: int = 1\n")
    f2.write_text("def test_x(): pass\n")

    parser = build_arg_parser()
    args = parser.parse_args(["--files", str(f1), str(f2), "--exclude-tests"])
    assert args.exclude_tests is True

    from src.review.cli import _collect_target_files

    targets = _collect_target_files(args)
    target_names = [p.name for p in targets]
    assert "app.py" in target_names
    assert "test_app.py" not in target_names

