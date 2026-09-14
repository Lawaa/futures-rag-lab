"""Report generation for embedding benchmarks.

Provides terminal table formatting, detailed Markdown reports, and JSON export.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

from .evaluator import BenchmarkResult, BenchmarkSuiteResult


class BenchmarkReporter:
    """Formats and exports benchmark evaluation results."""

    @staticmethod
    def format_terminal_table(suite: BenchmarkSuiteResult) -> str:
        """Format benchmark results as a clean ASCII table for terminal display."""
        headers = [
            "Model",
            f"Hit@{suite.top_k}",
            f"MRR@{suite.top_k}",
            f"NDCG@{suite.top_k}",
            "p50 (ms)",
            "p95 (ms)",
            "Idx (ch/s)",
            "RAM (MB)",
            "CPU %",
            "Status",
        ]

        rows: list[list[str]] = []
        for r in suite.results:
            if r.status == "success":
                rows.append([
                    r.model_name,
                    f"{r.hit_rate_at_k:.3f}",
                    f"{r.mrr_at_k:.3f}",
                    f"{r.ndcg_at_k:.3f}",
                    f"{r.latency_p50_ms:.1f}",
                    f"{r.latency_p95_ms:.1f}",
                    f"{r.indexing_throughput_chunks_per_sec:.1f}",
                    f"{r.peak_ram_mb:.0f}",
                    f"{r.avg_cpu_percent:.1f}%",
                    "[PASS]",
                ])
            else:
                rows.append([
                    r.model_name,
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    "[FAIL]",
                ])

        # Compute column widths
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, val in enumerate(row):
                col_widths[i] = max(col_widths[i], len(val))

        def make_row(values: list[str]) -> str:
            return " | ".join(val.ljust(col_widths[i]) for i, val in enumerate(values))

        separator = "-+-".join("-" * col_widths[i] for i in range(len(headers)))

        lines = [
            "=" * (sum(col_widths) + 3 * (len(headers) - 1)),
            "EMBEDDING MODEL BENCHMARK RESULTS",
            f"Corpus: {suite.total_documents} documents ({suite.total_chunks} chunks) | Top-K: {suite.top_k}",
            "=" * (sum(col_widths) + 3 * (len(headers) - 1)),
            make_row(headers),
            separator,
        ]
        for row in rows:
            lines.append(make_row(row))
        lines.append("=" * (sum(col_widths) + 3 * (len(headers) - 1)))

        # Add failed details if any
        failures = [r for r in suite.results if r.status != "success"]
        if failures:
            lines.append("\nFailures / Warnings:")
            for f in failures:
                lines.append(f"  * {f.model_name}: {f.error}")

        return "\n".join(lines)

    @classmethod
    def print_terminal_summary(cls, suite: BenchmarkSuiteResult) -> None:
        """Print the formatted summary table to stdout."""
        print("\n" + cls.format_terminal_table(suite) + "\n")

    @staticmethod
    def export_json(suite: BenchmarkSuiteResult, path: Path | str = "./data/benchmark_results.json") -> None:
        """Export raw benchmark execution results to JSON."""
        target_path = Path(path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(suite.model_dump_json(indent=2), encoding="utf-8")

    @staticmethod
    def export_markdown_report(
        suite: BenchmarkSuiteResult,
        path: Path | str = "./data/benchmark_report.md",
    ) -> None:
        """Generate a detailed Markdown evaluation report."""
        target_path = Path(path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        k = suite.top_k
        lines = [
            "# Embedding Model Benchmark Report",
            "",
            f"**Timestamp:** `{suite.timestamp}`  ",
            f"**Indexed Corpus:** {suite.total_documents} documents ({suite.total_chunks} chunks)  ",
            f"**Evaluation Rank Depth (Top-K):** {k}  ",
            "",
            "## 1. Executive Summary",
            "",
            "| Model | Retrieval Quality (Hit Rate) | MRR | NDCG | Latency p50 | Latency p95 | Indexing Throughput | Peak RAM | CPU % | Status |",
            "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
        ]

        for r in suite.results:
            if r.status == "success":
                lines.append(
                    f"| **{r.model_name}** | {r.hit_rate_at_k:.3f} | {r.mrr_at_k:.3f} | {r.ndcg_at_k:.3f} | "
                    f"{r.latency_p50_ms:.1f} ms | {r.latency_p95_ms:.1f} ms | "
                    f"{r.indexing_throughput_chunks_per_sec:.1f} chunks/s | {r.peak_ram_mb:.0f} MB | {r.avg_cpu_percent:.1f}% | ✅ Success |"
                )
            else:
                lines.append(
                    f"| **{r.model_name}** | - | - | - | - | - | - | - | - | ❌ Failed |"
                )

        lines.extend([
            "",
            "## 2. Metric Explanations",
            "",
            "- **Hit Rate@K**: Fraction of queries where the expected chunk appears in the top-K retrieved candidates (1.0 = perfect recall).",
            "- **MRR@K (Mean Reciprocal Rank)**: Evaluates ranking position; rewards placing relevant items at rank 1 (`1/1 = 1.0`), rank 2 (`1/2 = 0.5`), etc.",
            "- **NDCG@K (Normalized Discounted Cumulative Gain)**: Measures ranking quality with logarithmic position discounting (`1 / log2(rank + 1)`).",
            "- **Query Latency (p50 / p95)**: 50th and 95th percentile retrieval response times in milliseconds.",
            "- **Indexing Throughput**: Chunks embedded and saved into ChromaDB per second.",
            "- **Peak RAM Footprint**: Maximum Resident Set Size (RSS) observed across indexing and search.",
            "",
            "## 3. Hardware & Resource Profiles",
            "",
            "| Model | Indexing Duration | Throughput | Peak Process RAM | Peak GPU VRAM | Avg CPU % |",
            "| :--- | :---: | :---: | :---: | :---: | :---: |",
        ])

        for r in suite.results:
            if r.status == "success":
                vram_str = f"{r.peak_vram_mb:.0f} MB" if r.peak_vram_mb is not None else "N/A"
                lines.append(
                    f"| `{r.model_name}` | {r.indexing_time_sec:.2f}s | {r.indexing_throughput_chunks_per_sec:.1f} chunks/s | "
                    f"{r.peak_ram_mb:.0f} MB | {vram_str} | {r.avg_cpu_percent:.1f}% |"
                )
            else:
                lines.append(f"| `{r.model_name}` | Error | Error | Error | Error | Error |")

        # Failure details
        failures = [r for r in suite.results if r.status != "success"]
        if failures:
            lines.extend([
                "",
                "## 4. Diagnostics & Failures",
                "",
            ])
            for f in failures:
                lines.append(f"- **{f.model_name}**: `{f.error}`")

        target_path.write_text("\n".join(lines), encoding="utf-8")
