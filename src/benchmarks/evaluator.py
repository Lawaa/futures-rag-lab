"""Embedding model evaluator.

Builds temporary vector stores, runs benchmark queries, and computes retrieval
accuracy and hardware performance metrics across candidate embedding models.
"""

from __future__ import annotations

import datetime
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any, Sequence

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, Field

from ..embeddings import FastEmbedEmbeddings
from ..ingest import _load_documents, _split_documents
from ..logging_config import get_logger
from ..settings import Settings, get_settings
from .metrics import (
    HardwareMetrics,
    LatencyStats,
    ResourceTracker,
    compute_latency_stats,
    evaluate_query_retrieval,
)
from .synthetic_generator import BenchmarkDataset, assign_chunk_ids

logger = get_logger(__name__)

DEFAULT_BENCHMARK_MODELS = [
    "BAAI/bge-small-en-v1.5",
    "BAAI/bge-m3",
    "intfloat/multilingual-e5-large",
]

_MODEL_ALIASES: dict[str, str] = {
    "nomic-embed-text": "nomic-ai/nomic-embed-text-v1.5",
    "bge-small-en-v1.5": "BAAI/bge-small-en-v1.5",
    "bge-small": "BAAI/bge-small-en-v1.5",
    "bge-m3": "BAAI/bge-m3",
    "multilingual-e5-large": "intfloat/multilingual-e5-large",
}


class BenchmarkResult(BaseModel):
    """Evaluation result for a single embedding model."""

    model_name: str
    status: str = Field(default="success", description="'success' or 'failed'")
    top_k: int = Field(default=5)
    num_queries: int = Field(default=0)
    indexed_chunks: int = Field(default=0)
    indexing_time_sec: float = Field(default=0.0)
    indexing_throughput_chunks_per_sec: float = Field(default=0.0)
    hit_rate_at_k: float = Field(default=0.0)
    mrr_at_k: float = Field(default=0.0)
    ndcg_at_k: float = Field(default=0.0)
    latency_p50_ms: float = Field(default=0.0)
    latency_p95_ms: float = Field(default=0.0)
    latency_mean_ms: float = Field(default=0.0)
    peak_ram_mb: float = Field(default=0.0)
    avg_cpu_percent: float = Field(default=0.0)
    peak_vram_mb: float | None = Field(default=None)
    error: str | None = Field(default=None)


class BenchmarkSuiteResult(BaseModel):
    """Aggregate results for an entire benchmark suite run."""

    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    dataset_path: str | None = None
    total_documents: int = 0
    total_chunks: int = 0
    top_k: int = 5
    results: list[BenchmarkResult] = Field(default_factory=list)


def resolve_embedding_model(model_name: str, settings: Settings) -> Embeddings:
    """Resolve and instantiate an embedding model by name across backends."""
    normalized_name = _MODEL_ALIASES.get(model_name, model_name)

    # 1. Check if explicitly an Ollama model
    if normalized_name.startswith("ollama:") or normalized_name.startswith("ollama/"):
        target = normalized_name.split(":", 1)[1] if ":" in normalized_name else normalized_name.split("/", 1)[1]
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(model=target, base_url=settings.ollama_base_url)

    # 2. Check FastEmbed supported models
    try:
        from fastembed import TextEmbedding
        supported = {m["model"] for m in TextEmbedding.list_supported_models()}
        if normalized_name in supported:
            return FastEmbedEmbeddings(model_name=normalized_name)
    except Exception as err:
        logger.debug("FastEmbed model check failed: %s", err)

    # 3. Check SentenceTransformers if installed
    try:
        from sentence_transformers import SentenceTransformer

        class _SentenceTransformerAdapter(Embeddings):
            def __init__(self, target_model: str) -> None:
                self._st = SentenceTransformer(target_model)

            def embed_documents(self, texts: list[str]) -> list[list[float]]:
                embeddings = self._st.encode(texts, convert_to_numpy=True)
                return [row.tolist() for row in embeddings]

            def embed_query(self, text: str) -> list[float]:
                embedding = self._st.encode(text, convert_to_numpy=True)
                return embedding.tolist()

        return _SentenceTransformerAdapter(normalized_name)
    except ImportError:
        pass
    except Exception as err:
        logger.debug("SentenceTransformer initialization failed: %s", err)

    # 4. Check if Ollama has this model available locally
    try:
        from langchain_ollama import OllamaEmbeddings
        ollama_model = OllamaEmbeddings(model=normalized_name, base_url=settings.ollama_base_url)
        # Test trivial embedding
        ollama_model.embed_query("test")
        return ollama_model
    except Exception:
        pass

    raise ValueError(
        f"Embedding model '{model_name}' could not be loaded. "
        "It is not in FastEmbed's catalog, sentence-transformers is not installed, "
        f"and Ollama model '{model_name}' is not reachable at {settings.ollama_base_url}."
    )


class EmbeddingEvaluator:
    """Evaluates multiple embedding models on retrieval metrics and system utilization."""

    def __init__(
        self,
        models: Sequence[str] | None = None,
        dataset: BenchmarkDataset | None = None,
        settings: Settings | None = None,
        top_k: int = 5,
    ) -> None:
        self.models = list(models) if models else list(DEFAULT_BENCHMARK_MODELS)
        self.dataset = dataset or BenchmarkDataset()
        self.settings = settings or get_settings()
        self.top_k = top_k

    def load_corpus(self) -> tuple[list[Document], list[Document]]:
        """Load and chunk documents from data_path with deterministic IDs."""
        docs = _load_documents(self.settings)
        if not docs:
            raise RuntimeError(f"No documents found to index in {self.settings.data_path}")
        chunks = _split_documents(docs, self.settings)
        chunks = assign_chunk_ids(chunks)
        return docs, chunks

    def evaluate_model(
        self,
        model_name: str,
        chunks: list[Document],
    ) -> BenchmarkResult:
        """Run full indexing and retrieval evaluation for a single model."""
        logger.info("Evaluating embedding model: %s", model_name)

        # 1. Resolve embedding model
        try:
            embedding_function = resolve_embedding_model(model_name, self.settings)
        except Exception as err:
            logger.error("Failed to load model %s: %s", model_name, err)
            return BenchmarkResult(
                model_name=model_name,
                status="failed",
                top_k=self.top_k,
                error=str(err),
            )

        # 2. Build isolated temporary vector store and profile indexing
        temp_dir = tempfile.mkdtemp(prefix=f"rag_eval_{model_name.replace('/', '_')}_")
        temp_path = Path(temp_dir)
        try:
            with ResourceTracker() as tracker:
                vector_store = Chroma.from_documents(
                    documents=chunks,
                    embedding=embedding_function,
                    persist_directory=str(temp_path),
                    ids=[c.metadata["doc_id"] for c in chunks],
                )

            indexing_metrics = tracker.get_metrics()
            indexing_time = indexing_metrics.duration_sec
            throughput = len(chunks) / indexing_time if indexing_time > 0 else 0.0

            logger.info(
                "Indexed %d chunks with %s in %.2fs (%.1f chunks/s). Peak RAM: %.1fMB",
                len(chunks),
                model_name,
                indexing_time,
                throughput,
                indexing_metrics.peak_ram_mb,
            )

            # 3. Evaluate benchmark queries
            if not self.dataset.items:
                logger.warning("No benchmark queries provided for evaluation.")
                return BenchmarkResult(
                    model_name=model_name,
                    status="success",
                    top_k=self.top_k,
                    indexed_chunks=len(chunks),
                    indexing_time_sec=round(indexing_time, 3),
                    indexing_throughput_chunks_per_sec=round(throughput, 2),
                    peak_ram_mb=indexing_metrics.peak_ram_mb,
                    avg_cpu_percent=indexing_metrics.avg_cpu_percent,
                    peak_vram_mb=indexing_metrics.peak_vram_mb,
                )

            latencies: list[float] = []
            hit_rates: list[float] = []
            mrrs: list[float] = []
            ndcgs: list[float] = []

            with ResourceTracker() as query_tracker:
                for item in self.dataset.items:
                    t0 = time.perf_counter()
                    retrieved = vector_store.similarity_search(item.query, k=self.top_k)
                    latency = (time.perf_counter() - t0) * 1000.0
                    latencies.append(latency)

                    retrieved_ids = [doc.metadata.get("doc_id", "") for doc in retrieved]
                    retrieved_texts = [doc.page_content for doc in retrieved]

                    hr, mrr, ndcg = evaluate_query_retrieval(
                        retrieved_ids=retrieved_ids,
                        retrieved_texts=retrieved_texts,
                        expected_doc_id=item.expected_doc_id,
                        expected_chunk_text=item.expected_chunk_text,
                        k=self.top_k,
                    )
                    hit_rates.append(hr)
                    mrrs.append(mrr)
                    ndcgs.append(ndcg)

            query_metrics = query_tracker.get_metrics()
            lat_stats = compute_latency_stats(latencies)
            n_queries = len(self.dataset.items)

            mean_hr = sum(hit_rates) / n_queries if n_queries else 0.0
            mean_mrr = sum(mrrs) / n_queries if n_queries else 0.0
            mean_ndcg = sum(ndcgs) / n_queries if n_queries else 0.0

            # Overall peak RAM and max VRAM between indexing and querying
            combined_peak_ram = max(indexing_metrics.peak_ram_mb, query_metrics.peak_ram_mb)
            combined_vram = None
            if indexing_metrics.peak_vram_mb is not None or query_metrics.peak_vram_mb is not None:
                combined_vram = max(
                    indexing_metrics.peak_vram_mb or 0.0,
                    query_metrics.peak_vram_mb or 0.0,
                )

            avg_cpu = round((indexing_metrics.avg_cpu_percent + query_metrics.avg_cpu_percent) / 2.0, 2)

            return BenchmarkResult(
                model_name=model_name,
                status="success",
                top_k=self.top_k,
                num_queries=n_queries,
                indexed_chunks=len(chunks),
                indexing_time_sec=round(indexing_time, 3),
                indexing_throughput_chunks_per_sec=round(throughput, 2),
                hit_rate_at_k=round(mean_hr, 4),
                mrr_at_k=round(mean_mrr, 4),
                ndcg_at_k=round(mean_ndcg, 4),
                latency_p50_ms=round(lat_stats.p50_ms, 2),
                latency_p95_ms=round(lat_stats.p95_ms, 2),
                latency_mean_ms=round(lat_stats.mean_ms, 2),
                peak_ram_mb=round(combined_peak_ram, 2),
                avg_cpu_percent=avg_cpu,
                peak_vram_mb=round(combined_vram, 2) if combined_vram is not None else None,
            )
        finally:
            # Clean up temporary database directory
            shutil.rmtree(temp_path, ignore_errors=True)

    def run(self) -> BenchmarkSuiteResult:
        """Execute the benchmark suite across all requested models."""
        docs, chunks = self.load_corpus()
        results: list[BenchmarkResult] = []

        for model_name in self.models:
            result = self.evaluate_model(model_name, chunks)
            results.append(result)

        return BenchmarkSuiteResult(
            total_documents=len(docs),
            total_chunks=len(chunks),
            top_k=self.top_k,
            results=results,
        )
