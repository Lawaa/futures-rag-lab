# 📈 Modern SOTA Futures Trading RAG

A production-ready Retrieval-Augmented Generation (RAG) system built with **`uv`**, **LangChain**, **BAAI/bge-small-en-v1.5 Embeddings**, **ChromaDB**, and **Google Gemini 3.5 Flash Lite**.

---

## 🛠️ Tech Stack

- **Package & Environment Manager:** `uv` (Fastest Python tooling)
- **Embeddings:** `BAAI/bge-small-en-v1.5` (SOTA Retrieval Performance)
- **Vector Search:** ChromaDB
- **LLM:** Google Gemini 2.5 Flash

---

## ⚙️ Environment Configuration (`.env`)

Create a `.env` file in the root directory of the project. Currently, the system only requires your Google Gemini API key:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here

```

> 💡 **Note:** You can obtain a free API key at [Google AI Studio](https://aistudio.google.com/).

---

## 🚀 Quickstart Guide with `uv`

### 1. Install `uv` (if not already installed)

**Linux / macOS:**

```bash
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh

```

**Windows (PowerShell):**

```powershell
powershell -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"

```

### 2. Setup & Run

1. Clone the repository and navigate into the project folder.
2. Ensure your `.env` file is present in the root directory.
3. Place your PDF documents (e.g., CME trading guides) inside the `./data` folder.
4. Launch the application:

```powershell
uv run main.py

```

The system will automatically detect if `./chroma_db` exists. If not, it will automatically parse the documents in `./data`, generate vector embeddings, persist the database, and launch the interactive CLI query assistant.

---

## 💬 Example Queries

Once the interactive assistant is running (`uv run main.py`), try asking questions specific to your indexed futures trading documents:

### Margin & Liquidation

* `What is the difference between initial margin and maintenance margin?`
* `What happens when a trader receives a margin call?`

### Contract Mechanics

* `How does cash settlement differ from physical delivery in futures contracts?`
* `Explain how leverage works in index futures trading.`

### Risk Management & Trading

* `What is mark-to-market accounting and how is it calculated daily?`
* `What are the primary risks associated with holding a futures position overnight?`
