# Embedding Model Benchmark Report

**Timestamp:** `2026-09-14T11:59:45.919014+00:00`  
**Indexed Corpus:** 70 documents (134 chunks)  
**Evaluation Rank Depth (Top-K):** 5  

## 1. Executive Summary

| Model | Retrieval Quality (Hit Rate) | MRR | NDCG | Latency p50 | Latency p95 | Indexing Throughput | Peak RAM | CPU % | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **BAAI/bge-small-en-v1.5** | 1.000 | 0.833 | 0.877 | 9.2 ms | 43.7 ms | 13.1 chunks/s | 1763 MB | 522.5% | ✅ Success |
| **sentence-transformers/all-MiniLM-L6-v2** | 1.000 | 0.567 | 0.673 | 11.6 ms | 15.4 ms | 81.3 chunks/s | 752 MB | 361.1% | ✅ Success |

## 2. Metric Explanations

- **Hit Rate@K**: Fraction of queries where the expected chunk appears in the top-K retrieved candidates (1.0 = perfect recall).
- **MRR@K (Mean Reciprocal Rank)**: Evaluates ranking position; rewards placing relevant items at rank 1 (`1/1 = 1.0`), rank 2 (`1/2 = 0.5`), etc.
- **NDCG@K (Normalized Discounted Cumulative Gain)**: Measures ranking quality with logarithmic position discounting (`1 / log2(rank + 1)`).
- **Query Latency (p50 / p95)**: 50th and 95th percentile retrieval response times in milliseconds.
- **Indexing Throughput**: Chunks embedded and saved into ChromaDB per second.
- **Peak RAM Footprint**: Maximum Resident Set Size (RSS) observed across indexing and search.

## 3. Hardware & Resource Profiles

| Model | Indexing Duration | Throughput | Peak Process RAM | Peak GPU VRAM | Avg CPU % |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `BAAI/bge-small-en-v1.5` | 10.25s | 13.1 chunks/s | 1763 MB | N/A | 522.5% |
| `sentence-transformers/all-MiniLM-L6-v2` | 1.65s | 81.3 chunks/s | 752 MB | N/A | 361.1% |