# 📈 Modern SOTA Futures Trading RAG

A production-ready Retrieval-Augmented Generation (RAG) system built with **`uv`**, **LangChain**, **BAAI/bge-small-en-v1.5 Embeddings**, **ChromaDB**, and **Google Gemini 3.5 Flash Lite**.

---

## 🛠️ Tech Stack & Key Features

- **Package & Environment Manager:** `uv` (Fastest Python tooling)
- **Embeddings:** `BAAI/bge-small-en-v1.5` with Maximum Marginal Relevance (MMR) search
- **Vector Search:** ChromaDB
- **LLM:** Pluggable - hosted **Google Gemini** *or* a **local Ollama** model (e.g. Qwen) with no code changes
- **Credential Management:** OS-native keyring (`keyring`) - no plain text `.env` files required
- **Multi-Format Ingestion:** Auto-loads `.pdf`, `.txt`, and `.md` files from `./data`
- **Smart Data Auto-Sync:** Automated change detection via `.data_manifest.json` fingerprinting
- **Contextual Memory & Query Rewriting:** Reformulates ambiguous follow-up questions using chat history
- **Controlled Fallback:** Grounded answers strictly based on documents, with explicit notice when defaulting to general financial knowledge
- **Dual Interface:** Interactive CLI *and* a FastAPI HTTP service sharing the same core logic
- **Clean, Layered Architecture:** Centralized typed settings, dependency-injected services, and a pytest test suite

---

## 🏗️ Architecture

The code is organized into small, single-responsibility layers under `src/`:

| Module | Responsibility |
| --- | --- |
| `settings.py` | Centralized, typed configuration (env-overridable via `RAG_*`) |
| `credentials.py` | Secure API-key storage in the OS keyring |
| `llm.py` / `embeddings.py` / `vector_store.py` | Model & retriever factories |
| `manifest.py` / `ingest.py` | Change detection and the document ingestion pipeline |
| `prompts.py` / `models.py` | Prompt templates and domain data models |
| `rag_service.py` | `RagService` orchestration (rephrase -> retrieve -> answer) |
| `bootstrap.py` | Wires settings, DB and service together |
| `cli.py` / `api.py` | Interactive CLI and FastAPI interfaces |

Configuration can be overridden through environment variables (or a `.env` file),
e.g. `RAG_GEMINI_MODEL`, `RAG_RETRIEVER_K`, `RAG_CHUNK_SIZE`, `RAG_API_PORT`.

---

## 🧠 Choosing the LLM: Gemini or local Ollama

The assistant works with either a hosted Gemini model or a fully local model
served by Ollama (https://ollama.com) - controlled entirely by the
`RAG_LLM_PROVIDER` setting. The embeddings and retrieval stay the same; only the
answer-generation backend changes.

### Option A - Google Gemini (default)

No configuration needed; you'll be prompted for an API key on first run.

```bash
# optional overrides
export RAG_LLM_PROVIDER=gemini
export RAG_GEMINI_MODEL=gemini-3.5-flash-lite

```

### Option B - Local Ollama model (e.g. Qwen 7B)

Run everything offline with no API key:

```bash
# 1. Install & start Ollama ([https://ollama.com](https://ollama.com)), then pull a model
ollama pull qwen2.5:7b

# 2. Point the app at Ollama
export RAG_LLM_PROVIDER=ollama
export RAG_OLLAMA_MODEL=qwen2.5:7b         # any pulled model tag
export RAG_OLLAMA_BASE_URL=http://localhost:11434  # default

# 3. Run as usual
uv run main.py          # or: uv run serve.py

```

On startup the app verifies the Ollama server is reachable and the model is
pulled, printing clear instructions if not.

---

## 🔑 Security & API Key Setup

This project **does not require a `.env` file**.

On the first launch, the system will securely prompt you for your Google Gemini API key and store it in your operating system's native credential vault (e.g., **Windows Credential Manager**, **macOS Keychain**, or **Secret Service API** on Linux).

> 💡 **Note:** You can obtain a free API key at [Google AI Studio](https://aistudio.google.com/app/apikey).

---

## 🚀 Quickstart Guide with `uv`

### 1. Install `uv` (if not already installed)

**Linux / macOS:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

```

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"

```

### 2. Setup & Run

1. Clone the repository and navigate into the project folder.
2. Place your documents (`.pdf`, `.txt`, or `.md` files) inside the `./data` directory (e.g., trading guides, custom glossaries).
3. Launch the application:

```powershell
uv run main.py

```

---

## 🌐 Run as an HTTP API (FastAPI)

The same assistant is available as a FastAPI service:

```bash
uv run serve.py

```

Then open **`http://127.0.0.1:8000`** in a browser for the built-in chat web UI - a
clean, no-setup interface designed for non-technical users (suggested questions,
streaming-style typing indicator, sources shown per answer, and a "New chat"
button). Interactive API docs are at `http://127.0.0.1:8000/docs`.

Key endpoints:

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/` | Browser chat web UI |
| `GET` | `/health` | Liveness probe |
| `POST` | `/chat` | Answer a question, returns `{ answer, sources }` |
| `POST` | `/chat/stream` | Stream the answer token-by-token (plain text) |
| `DELETE` | `/sessions/{session_id}` | Clear a conversation's history |

```bash
curl -X POST http://127.0.0.1:8000/chat\
  -H "Content-Type: application/json" \
  -d '{"question": "What is initial margin?", "session_id": "demo"}'

```

> 💡 The API reads the Gemini key from `GEMINI_API_KEY` or the keyring. Run the CLI once (or set the env var) to store it before starting the server.

---

## 🧪 Testing

```bash
uv run pytest

```

---

## 🔄 Automatic Database Synchronization

The system calculates an MD5 fingerprint of the `./data` directory (tracking file names, sizes, and modification timestamps)
stored in `.data_manifest.json`.

* **No changes in `./data`:** Starts up instantly using the existing `./chroma_db`.
* **Files added, modified, or removed:** Automatically detects changes, rebuilds the vector database, and updates the
manifest seamlessly upon launch.

> 💡 **Note:** `.data_manifest.json` and `./chroma_db` are ignored in `.gitignore`.

---

## 💬 Memory & Multi-Turn Conversation Example

Follow-up questions are automatically rewritten into standalone queries before performing vector retrieval. Pronouns like
**"they"**, **"it"**, or **"that"** are resolved using preceding context.

```text
❓ Enter your trading query: what are spot contracts?

🟡 Thinking...

💡 Answer:
Based on the provided context, a spot contract is an agreement to buy or sell a financial instrument, commodity, or currency for immediate delivery and settlement on the spot date, which usually occurs within 1 to 2 business days. These transactions take place in the spot market and are not traded on standardized futures exchanges.

📚 Sources referenced:
  • a-traders-guide-to-futures.pdf (Page 14)
  • trading-glossary.txt
  • FuturesContractsFINAL.pdf (Page 9)

--------------------------------------------------

❓ Enter your trading query: how are they different from futures contracts?

🟡 Thinking...

💡 Answer:
Based on the provided context, spot contracts and futures contracts differ in several key ways:

* **Delivery and Settlement Timing:** A spot contract is an agreement for immediate delivery and settlement on the spot date (usually within 1 to 2 business days). In contrast, a futures contract is an agreement to buy or sell at a predetermined price on a specified future date.
* **Standardization:** Futures contracts are standardized, legally binding agreements, whereas spot contracts are for immediate transactions.
* **Exchange vs. Spot Market:** Spot contracts occur in the spot market and are not traded on standardized exchanges, whereas futures contracts are traded on regulated exchanges (such as the CME).
* **Daily Settlement:** Futures contracts require daily settlement (mark-to-market), a feature not associated with spot contracts.

📚 Sources referenced:
  • FuturesContractsFINAL.pdf (Page 6)
  • FuturesContractsFINAL.pdf (Page 2)
  • FuturesContractsFINAL.pdf (Page 8)

```

---

## 💬 Sample Query Ideas

Try asking questions specific to your indexed futures trading documents:

### Margin & Liquidation

* `What is the difference between initial margin and maintenance margin?`
* `What happens when a trader receives a margin call?`

### Contract Mechanics

* `How does cash settlement differ from physical delivery in futures contracts?`
* `Explain how leverage works in index futures trading.`

### Risk Management & Trading

* `What is mark-to-market accounting and how is it calculated daily?`
* `What are the primary risks associated with holding a futures position overnight?`
