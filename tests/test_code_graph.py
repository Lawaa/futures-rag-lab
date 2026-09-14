"""Unit and integration tests for the Code Knowledge Graph (CKG) and graph-aware review.

Tests:
- CodeGraphBuilder node and edge creation (CONTAINS, IMPORTS, CALLS)
- Multi-hop impact subgraph extraction (max_depth=1, 2)
- Markdown neighborhood impact context formatting
- Tier 1 instant security abort vs Tier 2 graph-aware review
- CLI --graph-depth argument handling
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage

from src.review.cli import build_arg_parser
from src.review.graph_builder import CodeGraphBuilder, _normalize_path
from src.review.hybrid_reviewer import HybridCodeReviewer
from src.settings import Settings


@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
    """Create a mini Python repository with interdependent modules."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    # Module A: defines helper and a class
    file_a = src_dir / "module_a.py"
    file_a.write_text(
        """\"\"\"Module A documentation.\"\"\"
import os
import sys

def helper_function(x: int) -> int:
    return x * 2

class ServiceA:
    def execute(self, val: int) -> int:
        return helper_function(val)
""",
        encoding="utf-8",
    )

    # Module B: calls ServiceA and helper_function
    file_b = src_dir / "module_b.py"
    file_b.write_text(
        """\"\"\"Module B documentation.\"\"\"
from src.module_a import ServiceA, helper_function

def caller_in_b() -> int:
    svc = ServiceA()
    res = svc.execute(10)
    return helper_function(res)
""",
        encoding="utf-8",
    )

    # Module C: calls caller_in_b (2-hop dependency from module_a)
    file_c = src_dir / "module_c.py"
    file_c.write_text(
        """\"\"\"Module C documentation.\"\"\"
from src.module_b import caller_in_b

def top_level_workflow() -> int:
    return caller_in_b()
""",
        encoding="utf-8",
    )

    return src_dir


def test_normalize_path() -> None:
    assert _normalize_path(Path("src") / "review" / "cli.py") == "src/review/cli.py"


def test_code_graph_builder_nodes_and_edges(temp_repo: Path) -> None:
    builder = CodeGraphBuilder(root_paths=[temp_repo])
    graph = builder.build_graph()

    assert graph.number_of_nodes() > 0
    assert graph.number_of_edges() > 0

    # Verify file nodes
    file_nodes = [n for n, d in graph.nodes(data=True) if d.get("kind") == "file"]
    assert len(file_nodes) == 3

    # Verify CONTAINS edges for functions & classes
    func_nodes = [n for n, d in graph.nodes(data=True) if d.get("kind") == "function"]
    assert any("helper_function" in n for n in func_nodes)
    assert any("caller_in_b" in n for n in func_nodes)
    assert any("top_level_workflow" in n for n in func_nodes)

    class_nodes = [n for n, d in graph.nodes(data=True) if d.get("kind") == "class"]
    assert any("ServiceA" in n for n in class_nodes)

    # Verify IMPORTS edges
    import_edges = [(u, v) for u, v, d in graph.edges(data=True) if d.get("relation") == "IMPORTS"]
    assert len(import_edges) >= 3


def test_code_graph_calls_relationship(temp_repo: Path) -> None:
    builder = CodeGraphBuilder(root_paths=[temp_repo])
    graph = builder.build_graph()

    call_edges = [(u, v) for u, v, d in graph.edges(data=True) if d.get("relation") == "CALLS"]
    assert len(call_edges) > 0

    # caller_in_b calls execute or helper_function
    callers = [u for u, v in call_edges]
    assert any("caller_in_b" in u for u in callers)


def test_get_impact_subgraph_depth_1_and_2(temp_repo: Path) -> None:
    builder = CodeGraphBuilder(root_paths=[temp_repo])
    builder.build_graph()

    file_a = temp_repo / "module_a.py"

    # Depth 1: module_a and immediate neighbors
    impact_d1 = builder.get_impact_subgraph([file_a], max_depth=1)
    assert impact_d1.total_nodes > 0
    assert "module_a.py" in str(impact_d1.seed_files)

    # Depth 2: includes 2-hop callers (e.g. module_c calling caller_in_b calling module_a)
    impact_d2 = builder.get_impact_subgraph([file_a], max_depth=2)
    assert impact_d2.total_nodes >= impact_d1.total_nodes
    assert len(impact_d2.markdown_context) > 0
    assert "Code Knowledge Graph Impact Analysis" in impact_d2.markdown_context


def test_impact_subgraph_empty_when_no_match(temp_repo: Path) -> None:
    builder = CodeGraphBuilder(root_paths=[temp_repo])
    builder.build_graph()

    impact = builder.get_impact_subgraph(["nonexistent_file.py"], max_depth=2)
    assert impact.total_nodes == 0
    assert "No dependencies found" in impact.markdown_context


def test_tier1_security_abort_short_circuits_llm(tmp_path: Path) -> None:
    """Ensure Tier 1 security check blocks execution without calling LLM or graph."""
    bad_file = tmp_path / "unsafe.py"
    bad_file.write_text(
        """def unsafe_execution(payload: str) -> None:
    eval(payload)
""",
        encoding="utf-8",
    )

    mock_llm = MagicMock()
    reviewer = HybridCodeReviewer(
        settings=Settings(),
        llm=mock_llm,
        root_paths=[tmp_path],
    )

    report = reviewer.review_file(bad_file, enable_llm_review=True)

    assert report.verdict == "BLOCKED"
    assert report.passes_safety is False
    assert report.llm_called is False
    assert report.graph_context is None
    # Verify LLM was NOT invoked
    mock_llm.invoke.assert_not_called()


def test_tier2_graph_aware_llm_review_called_when_safe(tmp_path: Path) -> None:
    """Ensure Tier 2 graph-aware review extracts impact and passes context to LLM."""
    safe_file = tmp_path / "safe.py"
    safe_file.write_text(
        """def compute_margin(balance: float, rate: float) -> float:
    return balance * rate
""",
        encoding="utf-8",
    )

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="[PASS] Clean implementation with low risk.")

    reviewer = HybridCodeReviewer(
        settings=Settings(),
        llm=mock_llm,
        root_paths=[tmp_path],
        graph_depth=2,
    )

    report = reviewer.review_file(safe_file, enable_llm_review=True)

    assert report.verdict == "PASS"
    assert report.passes_safety is True
    assert report.llm_called is True
    assert report.graph_context is not None
    assert "Code Knowledge Graph Impact Analysis" in report.graph_context
    assert report.llm_feedback == "[PASS] Clean implementation with low risk."

    # Verify LLM was called with formatted messages containing graph_context
    mock_llm.invoke.assert_called_once()
    called_messages = mock_llm.invoke.call_args[0][0]
    prompt_text = str(called_messages)
    assert "Code Knowledge Graph Impact Analysis" in prompt_text


def test_cli_parser_graph_depth() -> None:
    parser = build_arg_parser()
    args = parser.parse_args(["--graph-depth", "3"])
    assert args.graph_depth == 3
