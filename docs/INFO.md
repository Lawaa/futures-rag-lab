Listed directory futures-rag-lab
Listed directory src
Listed directory tests
Listed directory helper_tools
Viewed pyproject.toml:1-47
Viewed README.md:1-300
Viewed README.md:301-349
Listed directory docs
Viewed ARCHITECTURE.md:1-250
Viewed ARCHITECTURE.md:251-531
Viewed graph.py:1-250
Viewed graph.py:249-324
Viewed rag_service.py:1-250
Viewed rag_service.py:250-286
Viewed api.py:1-250
Viewed s3_service.py:1-250
Viewed settings.py:1-143

Here is a comprehensive breakdown of the **`futures-rag-lab`** codebase, structured to give you deep technical knowledge of every component, design pattern, and architectural decision, along with **tailored guidance on how to speak about this project in your interview** for the **Morgan Stanley Python / AI Platform Engineer** role.

---

# 📚 Overview of `futures-rag-lab`

`futures-rag-lab` is a production-grade, state-of-the-art **Retrieval-Augmented Generation (RAG) platform** designed for quantitative futures trading and financial analytics. It combines modern Python tooling (`uv`, `FastAPI`, `Pydantic v2`), agentic orchestration (`LangGraph`), vector search (`ChromaDB`, `bge-small-en-v1.5`), enterprise security (`keyring`), cloud storage (`AWS S3 boto3`), and pluggable LLM backends (**Google Gemini** or local **Ollama** models).

---

# 🏗️ Technical Architecture & Component Deep-Dive

The repository follows a clean, single-responsibility layered architecture under [`src/`](file:///c:/Users/Patrik/Documents/Work/futures-rag-lab/src):

```
                       ┌─────────────────────────┐
                       │   CLI / FastAPI Server  │
                       │   (src/cli.py, api.py)  │
                       └────────────┬────────────┘
                                    │
                       ┌────────────▼────────────┐
                       │       RagService        │
                       │  (src/rag_service.py)   │
                       └─────┬──────────────┬────┘
                             │              │
        ┌────────────────────▼────┐    ┌────▼────────────────────┐
        │     RetrievalGraph      │    │  Language Model & DBs   │
        │      (src/graph.py)     │    │  (llm.py, vector_store) │
        └─────────────────────────┘    └─────────────────────────┘
```

### 1. Agentic Retrieval Pipeline — [`src/graph.py`](file:///c:/Users/Patrik/Documents/Work/futures-rag-lab/src/graph.py)
* **Framework:** Built using **LangGraph** compiled state graphs (`StateGraph`).
* **State Machine Flow:**
  1. **Profile Routing (Optional):** Classifies incoming questions to match specific tenant/business personas using [`src/profiles.py`](file:///c:/Users/Patrik/Documents/Work/futures-rag-lab/src/profiles.py).
  2. **Query Preparation (Cross-Lingual):** Folds reference resolution (chat context) and domain-specific translation into a single LLM pass. Questions in Hungarian are automatically translated into canonical domain English terms matching the corpus.
  3. **Multi-Query Expansion & Reciprocal Rank Fusion (RRF) (Optional):** Fans out the query into $N$ semantic variants, executes parallel vector searches using Python's `ThreadPoolExecutor`, and fuses ranked document lists using RRF algorithm ($RRF\_Score = \sum \frac{1}{k + r}$).
  4. **Document Search:** Fetches candidate chunks using **Maximum Marginal Relevance (MMR)** in `ChromaDB` to maximize result diversity while preserving relevance.
  5. **Self-Correction & Quality Loop (Self-RAG / CRAG):** Retrieved passages are graded by the LLM. If relevant, it proceeds; if irrelevant and retry budget remains (`max_retrieval_retries`), the query is rewritten and retried.
* **Separation of Retrieval & Generation:** Generation is deliberately placed **outside** the retrieval graph. This allows the API to display sources immediately, stream tokens asynchronously, and avoid repeating expensive retrieval passes.
* **State Checkpointing:** Uses `langgraph-checkpoint-sqlite` to persist per-thread graph execution state across restarts.

### 2. Orchestration Core & Answer Grounding — [`src/rag_service.py`](file:///c:/Users/Patrik/Documents/Work/futures-rag-lab/src/rag_service.py)
* **Responsibility:** High-level coordinator linking `RetrievalGraph`, LLMs, conversation memory, and persistent storage.
* **Groundedness Check (Self-RAG Verification):** After an answer is generated, `_is_grounded()` evaluates whether the output is strictly backed by retrieved documents. Ungrounded answers are flagged, appended with an outside knowledge disclaimer, and stripped of misleading citations.
* **Live Progress Streaming:** `stream_events()` emits structured SSE JSON events (`status` $\rightarrow$ `token` $\rightarrow$ `done`) so front-ends can show progress indicators (e.g. `routing` $\rightarrow$ `preparing` $\rightarrow$ `retrieving` $\rightarrow$ `grading` $\rightarrow$ `answering`).

### 3. FastAPI HTTP Layer & Storage APIs — [`src/api.py`](file:///c:/Users/Patrik/Documents/Work/futures-rag-lab/src/api.py)
* **Framework:** FastAPI with Uvicorn ASGI server.
* **Features:**
  * Endpoint for non-blocking token streaming (`/chat/stream`) and event progress streaming (`/chat/events`).
  * Conversation history management (listing, fetching, renaming, deleting, and **pinning** to prevent auto-pruning).
  * Document management endpoints (`GET /documents`, `POST /documents/upload`, `DELETE /documents/{filename}`).
  * Lifespan setup handler (`_build_service_state`) that allows the web server to launch even if credentials are missing, reporting state to the frontend to drive a dynamic first-run wizard.

### 4. AWS S3 Integration — [`src/s3_service.py`](file:///c:/Users/Patrik/Documents/Work/futures-rag-lab/src/s3_service.py)
* **Cloud Storage:** Wraps AWS S3 using `boto3`.
* **In-Memory Streaming:** Converts S3 objects directly into `io.BytesIO` streams so LangChain loaders (`pypdf`, text splitters) can parse documents in-memory without disk I/O.
* **Sync & Fingerprinting:** Integrates with [`src/manifest.py`](file:///c:/Users/Patrik/Documents/Work/futures-rag-lab/src/manifest.py) to compare metadata fingerprints (MD5 / timestamps) between local/S3 files and the vector store to trigger automatic rebuilds only when documents change.

### 5. Config & Security — [`src/settings.py`](file:///c:/Users/Patrik/Documents/Work/futures-rag-lab/src/settings.py) & [`src/credentials.py`](file:///c:/Users/Patrik/Documents/Work/futures-rag-lab/src/credentials.py)
* **Configuration:** Centralized, strongly-typed settings powered by `pydantic-settings` (`Settings`), overrideable via `RAG_*` environment variables or `.env`.
* **Security:** API keys are never stored in raw text files; they are saved into OS native vaults (Windows Credential Manager / macOS Keychain / Linux Secret Service) using Python's `keyring` package. AWS secret keys follow standard `~/.aws/credentials` profile conventions.

### 6. Persistence & SQLite Store — [`src/conversation_store.py`](file:///c:/Users/Patrik/Documents/Work/futures-rag-lab/src/conversation_store.py)
* **Thread-safe SQLite Store:** Manages persistent history with automatic title generation, sliding window pruning (retains latest 15 conversations), and pinned thread protection.

---

# 🎯 How to Position This Project in Your Morgan Stanley Interview

The job description emphasizes **Python platform engineering, AI enablement/agents, cloud integration, data platforms, analytics, and enterprise system design**. Here is how to align this codebase directly with their key requirements:

| Job Requirement | Relevant Codebase Feature | What to highlight in your answers |
| :--- | :--- | :--- |
| **"Python platforms for quantitative & analytical models"** | Modular `RagService` platform, `pydantic` settings, `uv` environment tooling, concurrency via `ThreadPoolExecutor`. | Focus on how you structured the platform into clean, single-responsibility layers, managed dependencies cleanly with `uv`, and designed extensible interfaces for model/analytics execution. |
| **"AI-enabled solutions, LLMs & Agent-based integrations (e.g. MCP)"** | LangGraph agentic loop, Self-Correction, CRAG / Groundedness checking, Multi-Query expansion with RRF reranking. | Discuss how you built agentic workflows using **LangGraph state machines** instead of simple linear chains. Mention how **Model Context Protocol (MCP)** could be added to connect external quantitative market data tools directly into this graph. |
| **"Integrate analytics capabilities with enterprise systems"** | AWS S3 storage (`boto3`), OS Keyring API security, SQLite durable checkpointing, FastAPI streaming endpoints. | Explain enterprise readiness: zero plain-text secrets (using OS Keyring), cloud integration (streaming S3 files into memory via `BytesIO`), and resilience against provider rate limits. |
| **"Cross-functional collaboration & global hub (Budapest)"** | Hungarian & English bilingual support, domain-specific terminology translation in RAG query prep. | Highlight your ability to bridge technology and domain business requirements, creating bilingual capabilities catered for international hubs like Morgan Stanley Budapest. |

---

# 💬 Key Interview Questions & Talking Points

### Q1: "How do you handle AI hallucinations or poor retrieval in your RAG platform?"
> *"In `futures-rag-lab`, I implemented a multi-layered verification and self-correction architecture using LangGraph. First, at the retrieval stage, we run a self-corrective loop (Corrective RAG): retrieved documents are graded by an LLM node; if they fail quality criteria, a rewrite node reformulates the search query and retries retrieval up to a bounded retry count. Second, after answer generation, we run an explicit Groundedness Check (Self-RAG). If the generated answer contains ungrounded claims, the system strips misleading citations and flags the output with an outside-knowledge disclaimer."*

### Q2: "How do you scale RAG retrieval for complex financial queries?"
> *"Instead of relying on basic vector similarity, I used Maximum Marginal Relevance (MMR) search in ChromaDB to balance relevance with information diversity. For complex queries, we enable Multi-Query Expansion, which fans out the input into multiple complementary search queries, runs parallel vector lookups via a thread pool, and fuses the ranked document lists using Reciprocal Rank Fusion (RRF) reranking."*

### Q3: "How would you integrate MCP (Model Context Protocol) into this architecture?"
> *"In `src/graph.py`, our retrieval stage is already an agentic state graph. MCP can be integrated as an external tool execution layer. For example, when a trader asks for live futures market metrics or portfolio risk calculations, an MCP client node in LangGraph can query an external quantitative risk engine or market data feed, stream the structured tool output into the prompt context, and synthesize the final analytical response."*

### Q4: "How do you approach security and cloud architecture for enterprise data?"
> *"Enterprise platforms should never store plain-text API keys in configuration files. I integrated Python's `keyring` library to securely bind credentials to OS native keychains (Windows Credential Manager / macOS Keychain). For cloud storage, we built an S3 service using `boto3` that streams documents directly into `BytesIO` in-memory buffers so enterprise PDF/text documents can be processed and chunked without writing unencrypted temporary files to local disk."*

---

# 🚀 Next Steps / Interview Prep Tips
1. Run the test suite using `uv run pytest` to ensure everything passes smoothly on your machine.
2. Run `uv run main.py` or `uv run uvicorn src.api:app` to test both the guided CLI wizard and the web interface locally.
3. Be ready to walk through [`ARCHITECTURE.md`](file:///c:/Users/Patrik/Documents/Work/futures-rag-lab/docs/ARCHITECTURE.md) and [`src/graph.py`](file:///c:/Users/Patrik/Documents/Work/futures-rag-lab/src/graph.py) in a live coding or system design stage!