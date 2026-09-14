"""Retrieval and hardware performance metrics for embedding benchmarking.

Includes Hit Rate@K, MRR@K, NDCG@K, query latency percentiles (p50, p95),
and hardware resource tracking (Peak RAM, CPU %, VRAM) via psutil and PyTorch/pynvml.
"""

from __future__ import annotations

import math
import threading
import time
from typing import Any, Sequence

import psutil
from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
# Retrieval Metrics
# --------------------------------------------------------------------------- #

def compute_hit_rate_at_k(
    retrieved_items: Sequence[str],
    target_item: str,
    k: int = 5,
) -> float:
    """Compute Hit Rate@K for a single query.

    Returns 1.0 if the target item is within the top-K items, 0.0 otherwise.
    """
    top_k = list(retrieved_items)[:k]
    return 1.0 if target_item in top_k else 0.0


def compute_mrr_at_k(
    retrieved_items: Sequence[str],
    target_item: str,
    k: int = 5,
) -> float:
    """Compute Reciprocal Rank (RR@K) for a single query.

    Returns 1 / rank (1-indexed) if target is found within top-K, 0.0 otherwise.
    """
    top_k = list(retrieved_items)[:k]
    for rank, item in enumerate(top_k, start=1):
        if item == target_item:
            return 1.0 / rank
    return 0.0


def compute_ndcg_at_k(
    retrieved_items: Sequence[str],
    target_item: str,
    k: int = 5,
) -> float:
    """Compute Normalized Discounted Cumulative Gain (NDCG@K) for a single target.

    For a single relevant item, ideal DCG@K is 1 / log2(1 + 1) = 1.0.
    If the target item appears at rank r <= k, DCG@K = 1 / log2(r + 1).
    Therefore, NDCG@K = DCG@K / IDCG@K = 1 / log2(r + 1).
    """
    top_k = list(retrieved_items)[:k]
    for rank, item in enumerate(top_k, start=1):
        if item == target_item:
            return 1.0 / math.log2(rank + 1)
    return 0.0


def evaluate_query_retrieval(
    retrieved_ids: Sequence[str],
    retrieved_texts: Sequence[str],
    expected_doc_id: str,
    expected_chunk_text: str,
    k: int = 5,
) -> tuple[float, float, float]:
    """Evaluate retrieval quality for a single query using both IDs and text fallback.

    Returns (hit_rate, mrr, ndcg).
    """
    # Build list of matches: a retrieved candidate matches if doc_id matches
    # or if chunk text matches / contains significant overlap
    top_k_ids = list(retrieved_ids)[:k]
    top_k_texts = list(retrieved_texts)[:k]

    expected_clean_text = expected_chunk_text.strip()
    match_ranks: list[int] = []

    for rank, (doc_id, text) in enumerate(zip(top_k_ids, top_k_texts), start=1):
        if doc_id == expected_doc_id:
            match_ranks.append(rank)
            break
        # Text match fallback: exact or strong substring match
        clean_text = text.strip()
        if expected_clean_text and (
            expected_clean_text == clean_text
            or expected_clean_text in clean_text
            or clean_text in expected_clean_text
        ):
            match_ranks.append(rank)
            break

    if not match_ranks:
        return 0.0, 0.0, 0.0

    best_rank = match_ranks[0]
    hit_rate = 1.0
    mrr = 1.0 / best_rank
    ndcg = 1.0 / math.log2(best_rank + 1)
    return hit_rate, mrr, ndcg


# --------------------------------------------------------------------------- #
# Latency Metrics
# --------------------------------------------------------------------------- #

class LatencyStats(BaseModel):
    """Aggregated latency statistics in milliseconds."""

    p50_ms: float = Field(default=0.0, description="Median latency.")
    p95_ms: float = Field(default=0.0, description="95th percentile latency.")
    mean_ms: float = Field(default=0.0, description="Mean latency.")
    min_ms: float = Field(default=0.0, description="Minimum latency.")
    max_ms: float = Field(default=0.0, description="Maximum latency.")


def compute_latency_stats(latencies_ms: Sequence[float]) -> LatencyStats:
    """Calculate p50, p95, mean, min, and max latency from millisecond samples."""
    if not latencies_ms:
        return LatencyStats()

    sorted_latencies = sorted(latencies_ms)
    n = len(sorted_latencies)

    def percentile(p: float) -> float:
        index = int(math.ceil((p / 100.0) * n)) - 1
        index = max(0, min(index, n - 1))
        return sorted_latencies[index]

    return LatencyStats(
        p50_ms=percentile(50.0),
        p95_ms=percentile(95.0),
        mean_ms=sum(sorted_latencies) / n,
        min_ms=sorted_latencies[0],
        max_ms=sorted_latencies[-1],
    )


# --------------------------------------------------------------------------- #
# Hardware Resource Monitoring
# --------------------------------------------------------------------------- #

class HardwareMetrics(BaseModel):
    """System hardware utilization snapshot."""

    duration_sec: float = Field(default=0.0, description="Elapsed wall-clock time.")
    peak_ram_mb: float = Field(default=0.0, description="Peak resident RAM used in MB.")
    avg_cpu_percent: float = Field(default=0.0, description="Average CPU utilization percentage.")
    peak_vram_mb: float | None = Field(default=None, description="Peak GPU VRAM in MB if available.")


def get_vram_usage_mb() -> float | None:
    """Detect GPU VRAM usage via torch.cuda or pynvml if available."""
    try:
        import torch
        if torch.cuda.is_available():
            return torch.cuda.max_memory_allocated() / (1024 * 1024)
    except Exception:
        pass

    try:
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        return info.used / (1024 * 1024)
    except Exception:
        pass

    return None


class ResourceTracker:
    """Context manager for sampling RAM, CPU %, and VRAM during execution."""

    def __init__(self, sample_interval_sec: float = 0.05) -> None:
        self.sample_interval = sample_interval_sec
        self.process = psutil.Process()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._ram_samples: list[float] = []
        self._cpu_samples: list[float] = []
        self._vram_samples: list[float] = []
        self.start_time: float = 0.0
        self.end_time: float = 0.0

    def _sample_loop(self) -> None:
        # Prime cpu_percent
        self.process.cpu_percent(interval=None)
        while not self._stop_event.is_set():
            try:
                mem_mb = self.process.memory_info().rss / (1024 * 1024)
                self._ram_samples.append(mem_mb)
                cpu = self.process.cpu_percent(interval=None)
                self._cpu_samples.append(cpu)
                vram = get_vram_usage_mb()
                if vram is not None:
                    self._vram_samples.append(vram)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
            time.sleep(self.sample_interval)

    def __enter__(self) -> ResourceTracker:
        self._ram_samples.clear()
        self._cpu_samples.clear()
        self._vram_samples.clear()
        self._stop_event.clear()
        self.start_time = time.perf_counter()

        # Initial baseline sample
        try:
            self._ram_samples.append(self.process.memory_info().rss / (1024 * 1024))
            vram = get_vram_usage_mb()
            if vram is not None:
                self._vram_samples.append(vram)
        except Exception:
            pass

        self._thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.end_time = time.perf_counter()
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

        # Final sample
        try:
            self._ram_samples.append(self.process.memory_info().rss / (1024 * 1024))
            vram = get_vram_usage_mb()
            if vram is not None:
                self._vram_samples.append(vram)
        except Exception:
            pass

    def get_metrics(self) -> HardwareMetrics:
        """Produce HardwareMetrics from recorded samples."""
        duration = max(0.0001, self.end_time - self.start_time)
        peak_ram = max(self._ram_samples) if self._ram_samples else 0.0
        avg_cpu = sum(self._cpu_samples) / len(self._cpu_samples) if self._cpu_samples else 0.0
        peak_vram = max(self._vram_samples) if self._vram_samples else None

        return HardwareMetrics(
            duration_sec=duration,
            peak_ram_mb=round(peak_ram, 2),
            avg_cpu_percent=round(avg_cpu, 2),
            peak_vram_mb=round(peak_vram, 2) if peak_vram is not None else None,
        )
