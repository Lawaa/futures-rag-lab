"""Unit tests for the embedding benchmarking framework.

Verifies mathematical accuracy of Hit Rate@K, MRR@K, NDCG@K,
hardware tracking, dataset serialization, synthetic generation,
evaluation with mocked embeddings, and report generation.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.messages import AIMessage

from src.benchmarks.cli import build_arg_parser
from src.benchmarks.evaluator import (
    BenchmarkResult,
    BenchmarkSuiteResult,
    EmbeddingEvaluator,
    resolve_embedding_model,
)
from src.benchmarks.metrics import (
    ResourceTracker,
    compute_hit_rate_at_k,
    compute_latency_stats,
    compute_mrr_at_k,
    compute_ndcg_at_k,
    evaluate_query_retrieval,
)
from src.benchmarks.reporter import BenchmarkReporter
from src.benchmarks.synthetic_generator import (
    BenchmarkDataset,
    BenchmarkItem,
    SyntheticDatasetGenerator,
    assign_chunk_ids,
)
from src.settings import Settings


# --------------------------------------------------------------------------- #
# Math Metric Tests
# --------------------------------------------------------------------------- #

def test_hit_rate_at_k_present() -> None:
    items = ["doc_a", "doc_b", "doc_c", "doc_d", "doc_e"]
    assert compute_hit_rate_at_k(items, "doc_a", k=1) == 1.0
    assert compute_hit_rate_at_k(items, "doc_b", k=2) == 1.0
    assert compute_hit_rate_at_k(items, "doc_c", k=3) == 1.0
    assert compute_hit_rate_at_k(items, "doc_e", k=5) == 1.0


def test_hit_rate_at_k_absent_or_beyond_k() -> None:
    items = ["doc_a", "doc_b", "doc_c", "doc_d", "doc_e"]
    assert compute_hit_rate_at_k(items, "doc_c", k=2) == 0.0
    assert compute_hit_rate_at_k(items, "doc_z", k=5) == 0.0
    assert compute_hit_rate_at_k([], "doc_a", k=5) == 0.0


def test_mrr_at_k_exact_ranks() -> None:
    items = ["doc_a", "doc_b", "doc_c", "doc_d", "doc_e"]
    assert compute_mrr_at_k(items, "doc_a", k=5) == 1.0
    assert compute_mrr_at_k(items, "doc_b", k=5) == 0.5
    assert compute_mrr_at_k(items, "doc_c", k=5) == pytest.approx(1.0 / 3.0)
    assert compute_mrr_at_k(items, "doc_d", k=5) == 0.25
    assert compute_mrr_at_k(items, "doc_e", k=5) == 0.2


def test_mrr_at_k_beyond_k_or_missing() -> None:
    items = ["doc_a", "doc_b", "doc_c"]
    assert compute_mrr_at_k(items, "doc_c", k=2) == 0.0
    assert compute_mrr_at_k(items, "non_existent", k=5) == 0.0
    assert compute_mrr_at_k([], "doc_a", k=5) == 0.0


def test_ndcg_at_k_exact_formula() -> None:
    items = ["doc_1", "doc_2", "doc_3", "doc_4"]
    # Rank 1: 1 / log2(2) = 1.0
    assert compute_ndcg_at_k(items, "doc_1", k=4) == 1.0
    # Rank 2: 1 / log2(3) ≈ 0.63092975
    assert compute_ndcg_at_k(items, "doc_2", k=4) == pytest.approx(1.0 / math.log2(3))
    # Rank 3: 1 / log2(4) = 0.5
    assert compute_ndcg_at_k(items, "doc_3", k=4) == 0.5
    # Rank 4: 1 / log2(5) ≈ 0.43067655
    assert compute_ndcg_at_k(items, "doc_4", k=4) == pytest.approx(1.0 / math.log2(5))


def test_ndcg_at_k_beyond_k_or_missing() -> None:
    items = ["doc_1", "doc_2", "doc_3"]
    assert compute_ndcg_at_k(items, "doc_3", k=2) == 0.0
    assert compute_ndcg_at_k(items, "doc_unknown", k=5) == 0.0
    assert compute_ndcg_at_k([], "doc_1", k=5) == 0.0


def test_evaluate_query_retrieval_id_and_text_match() -> None:
    ids = ["doc_a", "doc_b", "doc_c"]
    texts = ["First content", "Target content here", "Third content"]

    # Match by ID at rank 1
    hr, mrr, ndcg = evaluate_query_retrieval(ids, texts, "doc_a", "Other", k=3)
    assert hr == 1.0
    assert mrr == 1.0
    assert ndcg == 1.0

    # Match by Text at rank 2
    hr, mrr, ndcg = evaluate_query_retrieval(ids, texts, "wrong_id", "Target content here", k=3)
    assert hr == 1.0
    assert mrr == 0.5
    assert ndcg == pytest.approx(1.0 / math.log2(3))

    # No match
    hr, mrr, ndcg = evaluate_query_retrieval(ids, texts, "wrong_id", "Completely unrelated", k=3)
    assert (hr, mrr, ndcg) == (0.0, 0.0, 0.0)


# --------------------------------------------------------------------------- #
# Latency & Hardware Monitoring Tests
# --------------------------------------------------------------------------- #

def test_compute_latency_stats() -> None:
    samples = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
    stats = compute_latency_stats(samples)
    assert stats.min_ms == 10.0
    assert stats.max_ms == 100.0
    assert stats.mean_ms == 55.0
    assert stats.p50_ms == 50.0
    assert stats.p95_ms == 100.0


def test_compute_latency_stats_empty() -> None:
    stats = compute_latency_stats([])
    assert stats.p50_ms == 0.0
    assert stats.mean_ms == 0.0


def test_resource_tracker_lifecycle() -> None:
    with ResourceTracker(sample_interval_sec=0.01) as tracker:
        # Simulate light work
        _ = sum(i * i for i in range(100_000))

    metrics = tracker.get_metrics()
    assert metrics.duration_sec > 0.0
    assert metrics.peak_ram_mb > 0.0
    assert metrics.avg_cpu_percent >= 0.0


# --------------------------------------------------------------------------- #
# Dataset Model & Serialization Tests
# --------------------------------------------------------------------------- #

def test_benchmark_dataset_save_load(tmp_path: Path) -> None:
    items = [
        BenchmarkItem(
            query="What is a futures contract?",
            expected_doc_id="glossary.txt:p0:c1",
            expected_chunk_text="A futures contract is an agreement to buy or sell...",
            answer="A standardized legal contract to buy or sell an asset.",
            source_file="glossary.txt",
        ),
        BenchmarkItem(
            query="Explain margin calls.",
            expected_doc_id="glossary.txt:p0:c2",
            expected_chunk_text="Margin call occurs when equity falls below maintenance level.",
            answer="A broker's demand for additional funds.",
            source_file="glossary.txt",
        ),
    ]
    dataset = BenchmarkDataset(items=items)
    file_path = tmp_path / "dataset.json"
    dataset.save(file_path)

    assert file_path.exists()
    loaded = BenchmarkDataset.load(file_path)
    assert len(loaded.items) == 2
    assert loaded.items[0].query == "What is a futures contract?"
    assert loaded.items[1].expected_doc_id == "glossary.txt:p0:c2"


def test_assign_chunk_ids() -> None:
    docs = [
        Document(page_content="Text 1", metadata={"source": "test/doc1.pdf", "page": 2}),
        Document(page_content="Text 2", metadata={"source": "test/doc2.txt"}),
    ]
    assigned = assign_chunk_ids(docs)
    assert assigned[0].metadata["doc_id"] == "doc1.pdf:p2:c0"
    assert assigned[1].metadata["doc_id"] == "doc2.txt:p0:c1"


# --------------------------------------------------------------------------- #
# Synthetic Generator Tests (with Mocked LLM)
# --------------------------------------------------------------------------- #

def test_synthetic_generator_with_mocked_llm() -> None:
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(
        content=json.dumps({
            "query": "What are the specs for E-mini S&P 500?",
            "answer": "Contract multiplier is $50 per index point.",
        })
    )

    dummy_chunk = Document(
        page_content="The E-mini S&P 500 futures contract multiplier is $50 times the S&P 500 stock index value.",
        metadata={"source": "data/guide.pdf", "page": 1, "doc_id": "guide.pdf:p1:c0"},
    )

    settings = Settings(_env_file=None)
    generator = SyntheticDatasetGenerator(settings=settings, llm=mock_llm)
    item = generator.generate_item_from_chunk(dummy_chunk)

    assert item is not None
    assert item.query == "What are the specs for E-mini S&P 500?"
    assert item.answer == "Contract multiplier is $50 per index point."
    assert item.expected_doc_id == "guide.pdf:p1:c0"
    assert "E-mini S&P 500" in item.expected_chunk_text


def test_synthetic_generator_skips_invalid_json() -> None:
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="Sorry, I cannot help with this.")

    dummy_chunk = Document(
        page_content="Long enough content to pass the length threshold for chunk processing.",
        metadata={"source": "data/guide.pdf", "page": 1, "doc_id": "guide.pdf:p1:c0"},
    )

    settings = Settings(_env_file=None)
    generator = SyntheticDatasetGenerator(settings=settings, llm=mock_llm)
    item = generator.generate_item_from_chunk(dummy_chunk)
    assert item is None


# --------------------------------------------------------------------------- #
# Embedding Evaluator Tests (Mocked Embedding Model)
# --------------------------------------------------------------------------- #

class MockEmbeddings(Embeddings):
    """Deterministic dummy embedding model for rapid, offline testing."""

    def __init__(self, dim: int = 8) -> None:
        self.dim = dim

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # Hash text to a stable unit-ish vector
        results = []
        for text in texts:
            val = float(hash(text) % 100) / 100.0
            results.append([val] * self.dim)
        return results

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


@patch("src.benchmarks.evaluator.resolve_embedding_model")
def test_embedding_evaluator_run(mock_resolve: MagicMock, tmp_path: Path) -> None:
    mock_resolve.return_value = MockEmbeddings()

    chunks = [
        Document(
            page_content="Futures contracts require initial margin.",
            metadata={"source": "glossary.txt", "doc_id": "glossary.txt:p0:c0"},
        ),
        Document(
            page_content="Options grant the right but not obligation.",
            metadata={"source": "glossary.txt", "doc_id": "glossary.txt:p0:c1"},
        ),
    ]

    dataset = BenchmarkDataset(
        items=[
            BenchmarkItem(
                query="What requires margin?",
                expected_doc_id="glossary.txt:p0:c0",
                expected_chunk_text="Futures contracts require initial margin.",
            )
        ]
    )

    settings = Settings(_env_file=None)
    evaluator = EmbeddingEvaluator(
        models=["mock-model"],
        dataset=dataset,
        settings=settings,
        top_k=2,
    )

    result = evaluator.evaluate_model("mock-model", chunks)
    assert result.status == "success"
    assert result.model_name == "mock-model"
    assert result.indexed_chunks == 2
    assert result.num_queries == 1
    assert result.indexing_throughput_chunks_per_sec >= 0.0
    assert result.peak_ram_mb > 0.0


def test_embedding_evaluator_unsupported_model() -> None:
    settings = Settings(_env_file=None)
    evaluator = EmbeddingEvaluator(
        models=["non_existent_crazy_model_xyz"],
        dataset=BenchmarkDataset(),
        settings=settings,
    )
    result = evaluator.evaluate_model(
        "non_existent_crazy_model_xyz",
        [Document(page_content="Content", metadata={"doc_id": "c1"})],
    )
    assert result.status == "failed"
    assert result.error is not None
    assert "could not be loaded" in result.error


# --------------------------------------------------------------------------- #
# Reporter Tests
# --------------------------------------------------------------------------- #

def test_benchmark_reporter_outputs(tmp_path: Path) -> None:
    suite = BenchmarkSuiteResult(
        total_documents=2,
        total_chunks=10,
        top_k=5,
        results=[
            BenchmarkResult(
                model_name="BAAI/bge-small-en-v1.5",
                status="success",
                top_k=5,
                num_queries=2,
                indexed_chunks=10,
                indexing_time_sec=1.2,
                indexing_throughput_chunks_per_sec=8.33,
                hit_rate_at_k=1.0,
                mrr_at_k=0.75,
                ndcg_at_k=0.82,
                latency_p50_ms=12.4,
                latency_p95_ms=18.6,
                latency_mean_ms=14.0,
                peak_ram_mb=340.0,
                avg_cpu_percent=42.5,
            ),
            BenchmarkResult(
                model_name="failed-model",
                status="failed",
                top_k=5,
                error="Model not installed",
            ),
        ],
    )

    # 1. Terminal table
    table_str = BenchmarkReporter.format_terminal_table(suite)
    assert "BAAI/bge-small-en-v1.5" in table_str
    assert "failed-model" in table_str
    assert "1.000" in table_str

    # 2. Markdown report
    md_path = tmp_path / "report.md"
    BenchmarkReporter.export_markdown_report(suite, md_path)
    assert md_path.exists()
    md_content = md_path.read_text(encoding="utf-8")
    assert "# Embedding Model Benchmark Report" in md_content
    assert "BAAI/bge-small-en-v1.5" in md_content

    # 3. JSON export
    json_path = tmp_path / "results.json"
    BenchmarkReporter.export_json(suite, json_path)
    assert json_path.exists()
    json_data = json.loads(json_path.read_text(encoding="utf-8"))
    assert json_data["total_chunks"] == 10
    assert len(json_data["results"]) == 2


# --------------------------------------------------------------------------- #
# CLI Parser Tests
# --------------------------------------------------------------------------- #

def test_cli_parser_defaults() -> None:
    parser = build_arg_parser()
    args = parser.parse_args([])
    assert "BAAI/bge-small-en-v1.5" in args.models
    assert args.top_k == 5
    assert args.generate_dataset is False
    assert args.dataset_path == "./data/benchmark_dataset.json"


def test_cli_parser_custom_flags() -> None:
    parser = build_arg_parser()
    args = parser.parse_args([
        "--models", "model_a", "model_b",
        "--top-k", "10",
        "--generate-dataset",
        "--dataset-path", "./test.json",
    ])
    assert args.models == ["model_a", "model_b"]
    assert args.top_k == 10
    assert args.generate_dataset is True
    assert args.dataset_path == "./test.json"
