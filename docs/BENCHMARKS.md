# Embedding Model Benchmarking Tool

Comprehensive guide for benchmarking text embedding models against domain documents in `futures-rag-lab`.

---

## 🎯 Overview & Objectives

In Retrieval-Augmented Generation (RAG) systems, selecting an embedding model involves balancing **retrieval quality** against **hardware footprint and latency**:
- A large model with high retrieval accuracy may impose unacceptable memory usage or latency for local deployment.
- A tiny, ultra-fast model may degrade semantic precision and result in hallucinated or incomplete answers.

The benchmarking tool inside `src/benchmarks/` provides automated, reproducible empirical testing of embedding models on domain documents in `./data`. It profiles:
1. **Retrieval Quality**: Hit Rate@K, Mean Reciprocal Rank (MRR@K), and Normalized Discounted Cumulative Gain (NDCG@K).
2. **Execution Latency**: Query retrieval latency percentiles (p50 and p95 in ms).
3. **Hardware Utilization**: Process peak RAM (MB via `psutil`), average CPU %, indexing throughput (chunks/sec), and GPU VRAM (MB via `torch.cuda` / `pynvml` if available).
4. **Overall Winners Podium**: Automatically scores and ranks candidate models to select the top 3 best performers for production.

> [!NOTE]
> **Zero Production Impact**: All benchmark indexing runs inside isolated temporary directories (`tempfile.mkdtemp`). Your production vector store (`./chroma_db`) is never overwritten, cleared, or modified.

---

## 🚀 Quickstart

### 1. Basic Benchmark Run (Using Existing Dataset)
Run evaluation on candidate models with rank depth $K = 5$:
```bash
uv run python -m src.benchmarks.cli --models BAAI/bge-small-en-v1.5 BAAI/bge-base-en-v1.5 sentence-transformers/all-MiniLM-L6-v2 --top-k 5
```

### 2. Generate a New Synthetic Evaluation Dataset
Auto-generate a synthetic Question-Context-Answer (QCA) dataset using domain documents and the configured LLM:
```bash
uv run python -m src.benchmarks.cli --generate-dataset --num-samples 15 --top-k 5
```

### 3. Full Help & Options
```bash
uv run python -m src.benchmarks.cli --help
```

---

## ⚙️ Command-Line Arguments

| Argument | Type | Default | Description |
| :--- | :---: | :--- | :--- |
| `--models` | list | `BAAI/bge-small-en-v1.5`, `BAAI/bge-m3`, `intfloat/multilingual-e5-large` | Target embedding models to evaluate. |
| `--top-k` | int | `5` | Rank evaluation depth $K$ for Hit Rate, MRR, and NDCG. |
| `--generate-dataset` | flag | `False` | Triggers synthetic dataset generation with the LLM before benchmarking. |
| `--dataset-path` | str | `./data/benchmark_dataset.json` | Path to load/persist the synthetic dataset. |
| `--num-samples` | int | `15` | Number of synthetic QCA items to generate when `--generate-dataset` is used. |
| `--report-path` | str | `./data/benchmark_report.md` | Path where the Markdown summary report will be exported. |
| `--results-path` | str | `./data/benchmark_results.json` | Path where raw machine-readable JSON metrics are saved. |

---

## 🧠 Supported Embedding Models

The tool dynamically resolves models across multiple backends:

### 1. FastEmbed ONNX Models (Default, Built-in)
FastEmbed runs lightweight, quantized ONNX models without requiring PyTorch:
- `BAAI/bge-small-en-v1.5` (Fast, lightweight English embedding model)
- `BAAI/bge-base-en-v1.5` (Higher semantic capacity base English model)
- `sentence-transformers/all-MiniLM-L6-v2` (Ultra-fast, minimal memory footprint)
- `snowflake/snowflake-arctic-embed-xs` (High performance, small footprint)
- `snowflake/snowflake-arctic-embed-m` (Top MTEB retrieval performance)
- `thenlper/gte-base` (General text embeddings base model)
- `nomic-ai/nomic-embed-text-v1.5` (Long-context 8192 token support)
- `intfloat/multilingual-e5-large` (100+ language support)

### 2. Local Ollama Embeddings
If an Ollama instance is running (`http://localhost:11434`), you can benchmark local Ollama models by prefixing with `ollama:`:
```bash
uv run python -m src.benchmarks.cli --models ollama:nomic-embed-text ollama:bge-m3
```

### 3. SentenceTransformers / HuggingFace
If `sentence-transformers` is installed in your Python environment, any HuggingFace model identifier can be passed directly.

---

## 📐 Evaluation Metrics Explained

### Retrieval Quality Metrics

1. **Hit Rate@K** (Recall@K):
   $$\text{Hit}@K = \begin{cases} 1.0 & \text{if expected chunk is within top } K \\ 0.0 & \text{otherwise} \end{cases}$$
   Measures whether the relevant chunk was retrieved at all.

2. **MRR@K (Mean Reciprocal Rank)**:
   $$\text{RR}@K = \begin{cases} \frac{1}{\text{rank}} & \text{if } 1 \le \text{rank} \le K \\ 0.0 & \text{otherwise} \end{cases}$$
   Rewards placing the target chunk higher up in the ranking (e.g. rank 1 = 1.0, rank 2 = 0.5, rank 3 = 0.33).

3. **NDCG@K (Normalized Discounted Cumulative Gain)**:
   $$\text{NDCG}@K = \begin{cases} \frac{1}{\log_2(\text{rank} + 1)} & \text{if } 1 \le \text{rank} \le K \\ 0.0 & \text{otherwise} \end{cases}$$
   Evaluates search ranking with smooth logarithmic position discounting.

### System & Hardware Metrics

1. **Query Retrieval Latency (p50 / p95)**:
   - Evaluated across benchmark queries in milliseconds.
   - Measures pure retrieval + embedding latency per query.
2. **Indexing Throughput**:
   - Chunks processed, embedded, and inserted into ChromaDB per second.
3. **Peak Process RAM (MB)**:
   - Maximum Resident Set Size (RSS) recorded during the run via `psutil`.
4. **Average CPU %**:
   - Multiprocess/thread average CPU utilization during execution.
5. **Peak GPU VRAM (MB)**:
   - GPU memory allocated via `torch.cuda` / `pynvml` (recorded if GPU acceleration is present).

### 🏆 Composite Score & Top 3 Podium Ranking

Models are ranked out of 100 points using a balanced formula:
$$\text{Score} = (0.45 \times \text{NDCG} + 0.30 \times \text{MRR} + 0.15 \times \text{HitRate}) \times 100 - \text{LatPenalty} + \text{TputBonus}$$
- **🥇 1st Place (Champion):** Best retrieval accuracy and ranking precision.
- **🥈 2nd Place (Runner-up):** Strong alternative balancing precision and latency.
- **🥉 3rd Place (Bronze):** High-efficiency candidate for constrained hardware.

---

## 📁 Output Files

The benchmark run generates three files (automatically ignored by git):

1. **`./data/benchmark_dataset.json`**:
   The synthetic evaluation dataset containing queries, expected chunk IDs, and ground-truth text.
2. **`./data/benchmark_report.md`**:
   A formatted Markdown report containing the Overall Winners podium, executive comparison table, metric definitions, and hardware profiles.
3. **`./data/benchmark_results.json`**:
   Raw, structured machine-readable JSON metrics for CI/CD tracking or automated regression testing.

---

## 🔄 Applying the Winner in Production

Once the benchmark identifies the optimal model (e.g. `BAAI/bge-base-en-v1.5`), update your `.env` or `src/settings.py`:
```env
# .env
RAG_EMBEDDING_MODEL=BAAI/bge-base-en-v1.5
```
Then re-index production documents:
```bash
uv run python -c "from src.settings import get_settings; from src.ingest import build_vector_db; build_vector_db(get_settings())"
```
