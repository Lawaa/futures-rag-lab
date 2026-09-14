"""Command-line interface for the embedding model benchmarking suite.

Uses Python's native argparse module to drive synthetic dataset generation,
model evaluation across candidates, and comprehensive report generation.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ..logging_config import get_logger
from ..settings import get_settings
from .evaluator import DEFAULT_BENCHMARK_MODELS, EmbeddingEvaluator
from .reporter import BenchmarkReporter
from .synthetic_generator import BenchmarkDataset, SyntheticDatasetGenerator

logger = get_logger(__name__)


def build_arg_parser() -> argparse.ArgumentParser:
    """Construct native argparse CLI parser."""
    parser = argparse.ArgumentParser(
        prog="python -m src.benchmarks.cli",
        description="Benchmark embedding models on retrieval accuracy and hardware footprint.",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=DEFAULT_BENCHMARK_MODELS,
        help="List of embedding model identifiers to benchmark (default: BAAI/bge-small-en-v1.5 BAAI/bge-m3 intfloat/multilingual-e5-large)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Rank depth K for Hit Rate@K, MRR@K, NDCG@K (default: 5)",
    )
    parser.add_argument(
        "--generate-dataset",
        action="store_true",
        help="Generate a new synthetic evaluation dataset using the configured LLM before running benchmarks.",
    )
    parser.add_argument(
        "--dataset-path",
        type=str,
        default="./data/benchmark_dataset.json",
        help="Path to load/save the synthetic benchmark dataset (default: ./data/benchmark_dataset.json)",
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        default=15,
        help="Number of synthetic QCA sample items to generate if --generate-dataset is used (default: 15)",
    )
    parser.add_argument(
        "--report-path",
        type=str,
        default="./data/benchmark_report.md",
        help="Path for the generated Markdown report (default: ./data/benchmark_report.md)",
    )
    parser.add_argument(
        "--results-path",
        type=str,
        default="./data/benchmark_results.json",
        help="Path for raw JSON execution results (default: ./data/benchmark_results.json)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if sys.stderr and hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = build_arg_parser()
    args = parser.parse_args(argv)

    settings = get_settings()
    dataset_path = Path(args.dataset_path)

    # 1. Dataset generation or loading
    dataset: BenchmarkDataset
    if args.generate_dataset or not dataset_path.exists():
        print(f"[*] Generating synthetic benchmark dataset ({args.num_samples} samples)...")
        try:
            generator = SyntheticDatasetGenerator(settings=settings)
            dataset = generator.generate(num_samples=args.num_samples, save_path=dataset_path)
            print(f"[+] Generated and saved dataset with {len(dataset.items)} items to {dataset_path}")
        except Exception as err:
            logger.error("Dataset generation failed: %s", err)
            print(f"[!] Error during dataset generation: {err}")
            return 1
    else:
        print(f"[*] Loading existing benchmark dataset from {dataset_path}...")
        try:
            dataset = BenchmarkDataset.load(dataset_path)
            print(f"[+] Loaded dataset with {len(dataset.items)} items.")
        except Exception as err:
            print(f"[!] Failed to load dataset: {err}")
            return 1

    if not dataset.items:
        print("[!] Warning: Benchmark dataset contains 0 items. Aborting evaluation.")
        return 1

    # 2. Run evaluation
    print(f"\n[*] Running benchmark evaluation for {len(args.models)} models (Top-K = {args.top_k})...")
    for m in args.models:
        print(f"    * {m}")

    evaluator = EmbeddingEvaluator(
        models=args.models,
        dataset=dataset,
        settings=settings,
        top_k=args.top_k,
    )
    suite_result = evaluator.run()
    suite_result.dataset_path = str(dataset_path)

    # 3. Output reports
    report_path = Path(args.report_path)
    results_path = Path(args.results_path)

    BenchmarkReporter.print_terminal_summary(suite_result)
    BenchmarkReporter.export_markdown_report(suite_result, report_path)
    BenchmarkReporter.export_json(suite_result, results_path)

    print(f"[+] Detailed Markdown report saved to: {report_path}")
    print(f"[+] Raw JSON metrics saved to:         {results_path}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
