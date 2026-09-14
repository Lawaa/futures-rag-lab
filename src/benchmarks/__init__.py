"""Modular Embedding Model Benchmarking Tool.

Evaluates embedding models on retrieval accuracy (Hit Rate, MRR, NDCG) and
hardware load (latency percentiles, peak RAM, avg CPU %, peak VRAM).
"""

from __future__ import annotations

from .evaluator import BenchmarkResult, BenchmarkSuiteResult, EmbeddingEvaluator
from .metrics import (
    HardwareMetrics,
    LatencyStats,
    ResourceTracker,
    compute_hit_rate_at_k,
    compute_latency_stats,
    compute_mrr_at_k,
    compute_ndcg_at_k,
    evaluate_query_retrieval,
)
from .reporter import BenchmarkReporter
from .synthetic_generator import BenchmarkDataset, BenchmarkItem, SyntheticDatasetGenerator

__all__ = [
    "BenchmarkItem",
    "BenchmarkDataset",
    "SyntheticDatasetGenerator",
    "compute_hit_rate_at_k",
    "compute_mrr_at_k",
    "compute_ndcg_at_k",
    "evaluate_query_retrieval",
    "compute_latency_stats",
    "LatencyStats",
    "HardwareMetrics",
    "ResourceTracker",
    "BenchmarkResult",
    "BenchmarkSuiteResult",
    "EmbeddingEvaluator",
    "BenchmarkReporter",
]
