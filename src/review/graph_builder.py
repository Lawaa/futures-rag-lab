"""Code Knowledge Graph (CKG) builder using Python's native AST and NetworkX.

Constructs an in-memory directed dependency graph across workspace Python files,
mapping Files, Classes, Functions, and Imports connected by CONTAINS, IMPORTS,
and CALLS relationships. Provides sub-graph extraction for impact-aware code reviews.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Sequence

import networkx as nx
from pydantic import BaseModel, Field

from ..logging_config import get_logger

logger = get_logger(__name__)


class GraphNode(BaseModel):
    """Metadata for a node in the Code Knowledge Graph."""

    id: str
    kind: str = Field(..., description="file, class, function, or module")
    name: str
    file_path: str = ""
    line: int = 0


class GraphEdge(BaseModel):
    """Directed edge between two entities in the Code Knowledge Graph."""

    source: str
    target: str
    relation: str = Field(..., description="CONTAINS, IMPORTS, or CALLS")


class ImpactSubgraphResult(BaseModel):
    """Result of querying the dependency graph for modified files."""

    seed_files: list[str]
    total_nodes: int
    total_edges: int
    impacted_callers: list[str] = Field(default_factory=list)
    impacted_callees: list[str] = Field(default_factory=list)
    imported_modules: list[str] = Field(default_factory=list)
    markdown_context: str = ""


def _normalize_path(path: str | Path) -> str:
    """Normalize file path to POSIX style for uniform graph node IDs."""
    return Path(path).as_posix()


class CodeGraphBuilder:
    """Builds and analyzes a directed Code Knowledge Graph (CKG) for Python projects."""

    def __init__(self, root_paths: Sequence[str | Path] | None = None) -> None:
        self.root_paths: list[Path] = [Path(p) for p in (root_paths or ["src"])]
        self.graph: nx.DiGraph = nx.DiGraph()
        self._symbol_to_nodes: dict[str, list[str]] = {}

    def build_graph(self) -> nx.DiGraph:
        """Scan target directories and build the full in-memory dependency graph."""
        self.graph.clear()
        self._symbol_to_nodes.clear()

        python_files = self._discover_files()
        logger.debug("Building Code Knowledge Graph across %d files...", len(python_files))

        # First pass: register files, classes, functions, and imports
        parsed_asts: list[tuple[str, ast.AST]] = []
        for file_path in python_files:
            rel_path = _normalize_path(file_path)
            try:
                content = file_path.read_text(encoding="utf-8")
                tree = ast.parse(content, filename=rel_path)
                parsed_asts.append((rel_path, tree))
                self._index_file_entities(rel_path, tree)
            except Exception as err:
                logger.debug("Failed to parse AST for %s: %s", rel_path, err)

        # Second pass: wire function calls across defined symbols
        for rel_path, tree in parsed_asts:
            self._index_function_calls(rel_path, tree)

        return self.graph

    def _discover_files(self) -> list[Path]:
        """Collect all .py files within configured root paths."""
        found: set[Path] = set()
        for root in self.root_paths:
            if root.is_file() and root.suffix == ".py":
                found.add(root)
            elif root.is_dir():
                found.update(root.rglob("*.py"))
        return sorted(found)

    def _index_file_entities(self, rel_path: str, tree: ast.AST) -> None:
        """Create File, Class, Function, and Import nodes and CONTAINS/IMPORTS edges."""
        file_node = f"file:{rel_path}"
        self.graph.add_node(
            file_node,
            kind="file",
            name=Path(rel_path).name,
            file_path=rel_path,
            line=1,
        )

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Import):
                self._record_import(file_node, node)
            elif isinstance(node, ast.ImportFrom):
                self._record_import_from(file_node, node)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._record_function(file_node, rel_path, node)
            elif isinstance(node, ast.ClassDef):
                self._record_class(file_node, rel_path, node)

    def _record_import(self, file_node: str, node: ast.Import) -> None:
        for alias in node.names:
            mod_node = f"module:{alias.name}"
            if not self.graph.has_node(mod_node):
                self.graph.add_node(mod_node, kind="module", name=alias.name)
            self.graph.add_edge(file_node, mod_node, relation="IMPORTS")

    def _record_import_from(self, file_node: str, node: ast.ImportFrom) -> None:
        module_name = node.module or ""
        mod_node = f"module:{module_name}"
        if not self.graph.has_node(mod_node):
            self.graph.add_node(mod_node, kind="module", name=module_name)
        self.graph.add_edge(file_node, mod_node, relation="IMPORTS")

    def _record_function(
        self, parent_node: str, rel_path: str, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> str:
        func_node = f"func:{rel_path}:{node.name}"
        self.graph.add_node(
            func_node,
            kind="function",
            name=node.name,
            file_path=rel_path,
            line=node.lineno,
        )
        self.graph.add_edge(parent_node, func_node, relation="CONTAINS")
        self._symbol_to_nodes.setdefault(node.name, []).append(func_node)
        return func_node

    def _record_class(self, parent_node: str, rel_path: str, node: ast.ClassDef) -> None:
        class_node = f"class:{rel_path}:{node.name}"
        self.graph.add_node(
            class_node,
            kind="class",
            name=node.name,
            file_path=rel_path,
            line=node.lineno,
        )
        self.graph.add_edge(parent_node, class_node, relation="CONTAINS")
        self._symbol_to_nodes.setdefault(node.name, []).append(class_node)

        # Record class methods
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._record_function(class_node, rel_path, child)

    def _index_function_calls(self, rel_path: str, tree: ast.AST) -> None:
        """Find ast.Call invocations inside functions and wire CALLS edges."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                caller_node = f"func:{rel_path}:{node.name}"
                if not self.graph.has_node(caller_node):
                    continue
                self._resolve_calls_in_body(caller_node, rel_path, node)

    def _resolve_calls_in_body(
        self, caller_node: str, rel_path: str, func_ast: ast.AST
    ) -> None:
        for sub_node in ast.walk(func_ast):
            if isinstance(sub_node, ast.Call):
                callee_name = self._get_call_target_name(sub_node.func)
                if not callee_name or callee_name == getattr(func_ast, "name", ""):
                    continue
                self._link_call_targets(caller_node, rel_path, callee_name)

    def _get_call_target_name(self, func_expr: ast.AST) -> str | None:
        if isinstance(func_expr, ast.Name):
            return func_expr.id
        if isinstance(func_expr, ast.Attribute):
            return func_expr.attr
        return None

    def _link_call_targets(self, caller_node: str, rel_path: str, callee_name: str) -> None:
        candidate_nodes = self._symbol_to_nodes.get(callee_name, [])
        if not candidate_nodes:
            return

        # Prefer targets defined in the same file first
        same_file_targets = [n for n in candidate_nodes if n.startswith(f"func:{rel_path}:")]
        target = same_file_targets[0] if same_file_targets else candidate_nodes[0]
        self.graph.add_edge(caller_node, target, relation="CALLS")

    def get_impact_subgraph(
        self,
        changed_files: Sequence[str | Path],
        max_depth: int = 2,
    ) -> ImpactSubgraphResult:
        """Extract the neighborhood dependency subgraph for the given modified files."""
        norm_files = [_normalize_path(p) for p in changed_files]
        seed_nodes = self._find_seed_nodes(norm_files)

        if not seed_nodes:
            return ImpactSubgraphResult(
                seed_files=norm_files,
                total_nodes=0,
                total_edges=0,
                markdown_context="No dependencies found for inspected files.",
            )

        # Multi-hop bidirectional traversal (both upstream callers and downstream dependencies)
        collected_nodes = self._traverse_neighbors(seed_nodes, max_depth)
        subgraph = self.graph.subgraph(collected_nodes).copy()

        callers, callees, modules = self._classify_impacts(subgraph, seed_nodes)
        markdown = self._render_impact_markdown(norm_files, seed_nodes, callers, callees, modules)

        return ImpactSubgraphResult(
            seed_files=norm_files,
            total_nodes=subgraph.number_of_nodes(),
            total_edges=subgraph.number_of_edges(),
            impacted_callers=sorted(callers),
            impacted_callees=sorted(callees),
            imported_modules=sorted(modules),
            markdown_context=markdown,
        )

    def _find_seed_nodes(self, norm_files: list[str]) -> set[str]:
        seeds: set[str] = set()
        for node, data in self.graph.nodes(data=True):
            file_path = data.get("file_path", "")
            if any(file_path == f or file_path.endswith(f) for f in norm_files):
                seeds.add(node)
        return seeds

    def _traverse_neighbors(self, seed_nodes: set[str], max_depth: int) -> set[str]:
        visited = set(seed_nodes)
        current_layer = set(seed_nodes)

        for _ in range(max_depth):
            next_layer = set()
            for node in current_layer:
                # Predecessors (callers, containing files)
                for pred in self.graph.predecessors(node):
                    if pred not in visited:
                        next_layer.add(pred)
                # Successors (callees, imported modules)
                for succ in self.graph.successors(node):
                    if succ not in visited:
                        next_layer.add(succ)
            visited.update(next_layer)
            current_layer = next_layer
            if not current_layer:
                break

        return visited

    def _classify_impacts(
        self, subgraph: nx.DiGraph, seed_nodes: set[str]
    ) -> tuple[set[str], set[str], set[str]]:
        callers: set[str] = set()
        callees: set[str] = set()
        modules: set[str] = set()

        for u, v, data in subgraph.edges(data=True):
            rel = data.get("relation", "")
            # Inbound calls to seed nodes from external nodes
            if rel == "CALLS" and v in seed_nodes and u not in seed_nodes:
                callers.add(u)
            # Outbound calls from seed nodes
            elif rel == "CALLS" and u in seed_nodes and v not in seed_nodes:
                callees.add(v)
            # Imported modules
            elif rel == "IMPORTS" and u in seed_nodes:
                modules.add(v.replace("module:", ""))

        return callers, callees, modules

    def _render_impact_markdown(
        self,
        norm_files: list[str],
        seed_nodes: set[str],
        callers: set[str],
        callees: set[str],
        modules: set[str],
    ) -> str:
        lines = [
            "### Code Knowledge Graph Impact Analysis",
            f"- **Target Modified File(s):** {', '.join(f'`{f}`' for f in norm_files)}",
            f"- **Internal Symbols Defined:** {len(seed_nodes)} node(s)",
            "",
        ]

        if callers:
            lines.append("#### ⚠️ Upstream Callers in Other Files (Breaking Change Risk):")
            for c in sorted(callers):
                lines.append(f"- `{c}`")
            lines.append("")
        else:
            lines.append("#### Upstream Callers:\n- None detected outside the modified file(s).\n")

        if callees:
            lines.append("#### 🔗 Outbound Called Functions:")
            for c in sorted(callees):
                lines.append(f"- `{c}`")
            lines.append("")

        if modules:
            lines.append(f"#### 📦 Imported Modules & Packages ({len(modules)}):")
            for m in sorted(modules)[:12]:
                lines.append(f"- `{m}`")
            if len(modules) > 12:
                lines.append(f"- ... and {len(modules) - 12} more")
            lines.append("")

        return "\n".join(lines).strip()
