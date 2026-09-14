"""Command-line interface for the local-first AST code review and safety guard system.

Uses Python's native argparse module to drive static analysis, staged file detection,
git pre-commit hook installation, and optional LLM architectural review.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from ..logging_config import get_logger
from ..settings import get_settings
from .ast_checker import is_test_file_path
from .git_hook import install_pre_commit_hook
from .hybrid_reviewer import HybridCodeReviewer, HybridReviewReport

logger = get_logger(__name__)


def build_arg_parser() -> argparse.ArgumentParser:
    """Construct native argparse CLI parser."""
    parser = argparse.ArgumentParser(
        prog="python -m src.review.cli",
        description="Local-first AST code review and safety gate with optional LLM architectural feedback.",
    )
    parser.add_argument(
        "--files",
        nargs="*",
        default=[],
        help="List of Python files or directories to inspect.",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Inspect only git staged Python files (git diff --cached --name-only).",
    )
    parser.add_argument(
        "--llm-review",
        action="store_true",
        help="Run optional second-stage LLM architectural review on inspected files.",
    )
    parser.add_argument(
        "--install-hook",
        action="store_true",
        help="Install the pre-commit safety hook into .git/hooks/pre-commit.",
    )
    parser.add_argument(
        "--complexity-threshold",
        type=int,
        default=10,
        help="Cyclomatic complexity limit before raising a warning (default: 10).",
    )
    parser.add_argument(
        "--graph-depth",
        type=int,
        default=2,
        help="Neighbor traversal depth in the Code Knowledge Graph (default: 2).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail (exit code 1) on warnings as well as blocking security violations.",
    )
    parser.add_argument(
        "--exclude-tests",
        action="store_true",
        help="Exclude test files (e.g. tests/ directory, test_*.py) from the review.",
    )
    return parser


def get_staged_python_files() -> list[Path]:
    """Retrieve list of staged Python files via git."""
    try:
        output = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=d"],
            text=True,
            encoding="utf-8",
            stderr=subprocess.DEVNULL,
        )
        staged: list[Path] = []
        for line in output.splitlines():
            clean = line.strip()
            if clean.endswith(".py"):
                p = Path(clean)
                if p.exists():
                    staged.append(p)
        return staged
    except Exception as err:
        logger.warning("Could not query git staged files: %s", err)
        return []


def discover_python_files(targets: list[str]) -> list[Path]:
    """Resolve file paths and directories to a list of Python files."""
    results: set[Path] = set()
    for item in targets:
        p = Path(item)
        if p.is_file() and p.suffix == ".py":
            results.add(p)
        elif p.is_dir():
            results.update(p.rglob("*.py"))
    return sorted(results)


def _configure_console_io() -> None:
    """Safely configure stdout/stderr UTF-8 encoding on Windows."""
    for stream in (sys.stdout, sys.stderr):
        if stream and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, OSError, ValueError) as err:
                logger.debug("Console stream reconfigure omitted: %s", err)


def _collect_target_files(args: argparse.Namespace) -> list[Path]:
    """Determine target Python files to review based on CLI flags."""
    if args.staged:
        files = get_staged_python_files()
    elif args.files:
        files = discover_python_files(args.files)
    else:
        files = discover_python_files(["src", "tests"])

    if getattr(args, "exclude_tests", False):
        files = [p for p in files if not is_test_file_path(p)]
    return files


def _display_report(report: HybridReviewReport) -> None:
    """Print results for a single file."""
    print(f"\n[{report.verdict}] {report.file_path}")
    if report.ast_result.issues:
        for issue in report.ast_result.issues:
            prefix = "[BLOCKING]" if issue.severity == "BLOCKING" else "[WARN]"
            print(f"   {prefix} Line {issue.line_number}:{issue.column} - {issue.message}")
    else:
        print("   [+] All AST safety and structural checks passed.")

    if report.impact_summary:
        nodes_cnt = report.impact_summary.get("total_nodes", 0)
        edges_cnt = report.impact_summary.get("total_edges", 0)
        callers = report.impact_summary.get("impacted_callers", [])
        callees = report.impact_summary.get("impacted_callees", [])
        print(f"   [CKG Impact] Neighborhood: {nodes_cnt} node(s), {edges_cnt} edge(s) | Upstream callers: {len(callers)} | Outbound calls: {len(callees)}")

    if report.llm_feedback:
        print("\n   --- LLM Architectural Review Feedback ---")
        for line in report.llm_feedback.splitlines():
            print(f"   {line}")
        print("   ----------------------------------------")


def _print_review_summary(reports: list[HybridReviewReport]) -> tuple[int, int, int]:
    """Print full terminal review results and return counts (clean, warnings, blocked)."""
    blocked_count = 0
    warning_count = 0
    clean_count = 0

    print("\n" + "=" * 80)
    print("CODE REVIEW & SAFETY GUARD RESULTS")
    print("=" * 80)

    for report in reports:
        _display_report(report)
        if report.verdict == "BLOCKED":
            blocked_count += 1
        elif report.verdict == "WARNINGS":
            warning_count += 1
        else:
            clean_count += 1

    print("\n" + "=" * 80)
    print(
        f"SUMMARY: {len(reports)} inspected | {clean_count} passed | "
        f"{warning_count} with warnings | {blocked_count} blocked"
    )
    print("=" * 80 + "\n")

    return clean_count, warning_count, blocked_count


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    _configure_console_io()
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.install_hook:
        try:
            hook_path = install_pre_commit_hook()
            print(f"[+] Successfully installed pre-commit hook at: {hook_path}")
            return 0
        except Exception as err:
            print(f"[!] Failed to install pre-commit hook: {err}")
            return 1

    files_to_check = _collect_target_files(args)
    if not files_to_check:
        msg = "[*] No staged Python files detected for review." if args.staged else "[!] No Python files found."
        print(msg)
        return 0

    print(f"[*] Inspecting {len(files_to_check)} file(s) with AST Safety Gate...")
    if args.llm_review:
        print(f"[*] Graph-Aware LLM Review enabled (neighborhood depth: {args.graph_depth}).")

    reviewer = HybridCodeReviewer(
        settings=get_settings(),
        complexity_threshold=args.complexity_threshold,
        graph_depth=args.graph_depth,
    )
    reports = reviewer.review_files(files_to_check, enable_llm_review=args.llm_review)
    _, warning_count, blocked_count = _print_review_summary(reports)

    if blocked_count > 0:
        print("[!] Commit rejected: One or more files violated safety guards.")
        return 1
    if args.strict and warning_count > 0:
        print("[!] Strict mode failure: Warnings detected.")
        return 1

    print("[+] All safety checks passed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
