# Repurposing the Assistant for a New Domain

This guide shows developers how to turn this project from a *futures trading*
assistant into a knowledge base for **any** domain — for example a **law firm**
or a **healthcare provider** — and, if you want, how to serve several such
businesses from a **single deployment** (white-label / multi-tenant).

The system was designed to be **domain-agnostic**: the retrieval pipeline,
grounding, self-correction, and UI are generic. Only three things are truly
domain-specific:

1. **The documents** in [`data/`](../data) (the knowledge itself).
2. **The persona** — the assistant's system prompt and display name.
3. **The surface text** — UI labels, example questions, and app branding.

Everything else (chunking, embeddings, retrieval, translation, groundedness,
conversation memory) works unchanged.

> TL;DR: swap the documents, set a persona via `profiles.json`, tweak the UI
> strings, and — for multi-tenant — enable routing. No pipeline code changes.

---

## 1. Swap the knowledge base

The assistant only knows what is in [`data/`](../data).

1. Delete the sample file(s) in `data/` (e.g. `trading-glossary.txt`).
2. Drop in your own `.pdf`, `.txt`, or `.md` files — contracts and case
   summaries for a law firm; clinical guidelines and patient-education leaflets
   for a healthcare provider.
3. Start the app. The change-detection manifest notices the new files and
   **rebuilds the vector index automatically** on launch. No manual re-index
   command is needed.

**Tips**

- Prefer clean, text-based PDFs. Scanned/image-only PDFs have no extractable
  text and will not be indexed (add an OCR step upstream if needed).
- Keep documents authoritative and current — the assistant grounds its answers
  in whatever you provide, so stale content produces stale answers.
- Adjust `RAG_CHUNK_SIZE` / `RAG_CHUNK_OVERLAP` if your documents are unusually
  short (smaller chunks) or long and narrative (larger chunks).

---

## 2. Set the persona (single business)

The assistant's voice comes from a **system prompt**. The cleanest, code-free way
to change it is a `profiles.json` file at the repo root (path configurable via
`RAG_PROFILES_PATH`). Even for a single business, one profile is enough:

```json
[
  {
    "id": "default",
    "name": "Acme Law Assistant",
    "description": "Employment-law knowledge base for Acme Law LLP.",
    "system_prompt": "You are a legal information assistant for Acme Law LLP. Explain concepts from the firm's documents clearly and precisely. You provide general legal information, not legal advice, and you never invent case citations."
  }
]
```

- `system_prompt` **overrides** the built-in persona used during answer
  generation.
- The shared grounding rules (answer from context; disclaim when using outside
  knowledge) are always appended automatically, so groundedness handling keeps
  working for every persona.
- `id: "default"` matches the default `RAG_PROFILE`, so this profile is active
  out of the box.

> If you never add a `profiles.json`, a built-in `default` profile is used and
> the persona falls back to the generic template in
> [`src/prompts.py`](../src/prompts.py) (`DEFAULT_PERSONAS`). Editing that
> dictionary is the alternative if you'd rather bake the persona into code.

---

## 3. Rebrand the surface text

These strings are user-facing and still mention futures trading. Update them for
your domain:

| What | Where |
| --- | --- |
| Web UI title, header, subtitle, welcome text, example questions | [`src/static/index.html`](../src/static/index.html) — the `I18N` object (`en` and `hu` blocks) |
| App icon / favicon | [`src/static/assets/`](../src/static/assets) (replace `icon.png`) |
| Default persona (if not using `profiles.json`) | [`src/prompts.py`](../src/prompts.py) — `DEFAULT_PERSONAS` |
| Desktop app folder name | [`desktop/backend/entry.py`](../desktop/backend/entry.py) — `APP_DIR_NAME` |
| CLI banner / catalog text | [`src/i18n.py`](../src/i18n.py) |

In `index.html`, at minimum update `docTitle`, `headerTitle`, `headerSubtitle`,
`welcomeText`, and the `suggestions` array (the example question chips) in **both**
the `en` and `hu` dictionaries. Pick example questions your documents can
actually answer — they set user expectations and double as a smoke test.

---

## 4. Serve several businesses from one build (multi-tenant)

To run one deployment that answers as **different** businesses, define multiple
profiles and turn on routing:

```json
[
  {
    "id": "law",
    "name": "Acme Law Assistant",
    "description": "Contracts, employment law and compliance for a law firm.",
    "system_prompt": "You are a legal information assistant. Be precise, cite the firm's documents, and never give personalised legal advice."
  },
  {
    "id": "health",
    "name": "Wellspring Health Assistant",
    "description": "Clinical guidelines and patient education for a healthcare provider.",
    "system_prompt": "You are a healthcare information assistant. Use plain language, be cautious, and always recommend consulting a clinician for personal medical decisions."
  }
]
```

Enable automatic routing:

```bash
export RAG_ENABLE_PROFILE_ROUTING=true
```

With routing on and more than one profile defined, the retrieval graph adds a
**route** step: it classifies each incoming question against the profile
`description`s and answers with the matching profile's persona. Write clear,
distinctive descriptions — that text is exactly what the router sees.

**Choosing per-tenant vs. per-question routing**

- **Per-question routing** (above) is best when one set of documents spans
  several domains and you want the persona to follow the topic.
- **Per-tenant pinning** — if each business should be fully isolated, run one
  process per tenant instead, each with `RAG_ENABLE_PROFILE_ROUTING=false` and a
  fixed `RAG_PROFILE=<id>`. This guarantees a tenant only ever answers in its own
  voice.

> Note: all profiles currently share the **same document index**. If tenants
> must not see each other's documents, run separate processes with separate
> `RAG_DATA_PATH` / `RAG_DB_PATH` directories (see §6).

---

## 5. Non-English or multilingual corpora

The pipeline is cross-lingual: questions are translated into the **corpus
language** before searching, so users can ask in any language.

- Set `RAG_RETRIEVAL_LANGUAGE` to the language your documents are written in
  (`en` or `hu` today; extend `LANGUAGE_NAMES` in
  [`src/prompts.py`](../src/prompts.py) to add more).
- Set `RAG_LANGUAGE` to the language you want answers and the UI in.
- The default embedding model (`BAAI/bge-small-en-v1.5`) is English-optimised.
  For a non-English or multilingual corpus, switch to a multilingual embedding
  model via `RAG_EMBEDDING_MODEL` (e.g. a `multilingual-e5` or `bge-m3` model)
  and re-index.

---

## 6. Useful configuration knobs

All settings live in [`src/settings.py`](../src/settings.py) and are overridable
via `RAG_*` environment variables or a `.env` file. The ones most relevant when
repurposing:

| Setting (env var) | Purpose |
| --- | --- |
| `RAG_DATA_PATH` | Where source documents live |
| `RAG_DB_PATH` | Where the vector index + checkpoints are stored |
| `RAG_PROFILES_PATH` | Location of `profiles.json` |
| `RAG_PROFILE` | Active profile when routing is off |
| `RAG_ENABLE_PROFILE_ROUTING` | Auto-route each question to a profile |
| `RAG_LANGUAGE` / `RAG_RETRIEVAL_LANGUAGE` | Answer/UI language and corpus language |
| `RAG_EMBEDDING_MODEL` | Embedding model (change for non-English corpora) |
| `RAG_CHUNK_SIZE` / `RAG_CHUNK_OVERLAP` | Document splitting granularity |
| `RAG_RETRIEVER_K` / `RAG_RETRIEVER_FETCH_K` | How many chunks to return / consider |
| `RAG_ENABLE_MULTI_QUERY` / `RAG_MULTI_QUERY_COUNT` | Fan-out + rerank for broader recall |
| `RAG_ENABLE_GROUNDEDNESS_CHECK` | Verify answers are supported by the documents |
| `RAG_ENABLE_SELF_CORRECTION` / `RAG_MAX_RETRIEVAL_RETRIES` | Grade-and-retry loop |
| `RAG_LLM_PROVIDER` | `gemini` (hosted) or `ollama` (local, private) |
| `RAG_USE_S3_STORAGE` | Enable AWS S3 storage mode (`true` / `false`) |
| `RAG_AWS_S3_BUCKET_NAME` | AWS S3 bucket name (default: `futures-rag-lab-docs`) |

> For sensitive domains (legal, healthcare), consider `RAG_LLM_PROVIDER=ollama`
> so no document text or questions leave the machine.

---

## 7. Worked example — a law firm

1. Put the firm's public guides and policy PDFs in `data/`.
2. Create `profiles.json`:
   ```json
   [
     {
       "id": "default",
       "name": "Acme Law Assistant",
       "description": "Employment-law knowledge base for Acme Law LLP.",
       "system_prompt": "You are a legal information assistant for Acme Law LLP. Answer only from the firm's documents, be precise about jurisdictions and dates, provide general legal information (not advice), and never fabricate case citations."
     }
   ]
   ```
3. In [`src/static/index.html`](../src/static/index.html), set the title to
   "Acme Law Assistant" and replace the example questions with, e.g.:
   - "What notice period applies to a fixed-term contract?"
   - "How should overtime be recorded under our policy?"
4. Replace `src/static/assets/icon.png` with the firm's logo.
5. (Optional) `export RAG_LLM_PROVIDER=ollama` to keep everything on-premises.
6. `uv run main.py` → the index rebuilds from the new documents and the assistant
   answers as the firm.

For a healthcare provider, repeat with clinical documents, a cautious
patient-facing `system_prompt`, and medical example questions.

---

## 8. Repurposing checklist

- [ ] Replaced the documents in `data/`
- [ ] Wrote `profiles.json` with a domain-appropriate `system_prompt`
- [ ] Updated `index.html` title, subtitle, welcome text, and example questions (EN + HU)
- [ ] Replaced the app icon in `src/static/assets/`
- [ ] Set `RAG_RETRIEVAL_LANGUAGE` (and a multilingual `RAG_EMBEDDING_MODEL` if needed)
- [ ] Chose an LLM provider (`gemini` vs `ollama`) appropriate to your data sensitivity
- [ ] (Multi-tenant) Added multiple profiles and set `RAG_ENABLE_PROFILE_ROUTING=true`
- [ ] Renamed `APP_DIR_NAME` in `desktop/backend/entry.py` if you ship a desktop build
- [ ] Ran `uv run pytest` and verified answers against your documents

See [ARCHITECTURE.md](ARCHITECTURE.md) for how the pieces fit together and
[DESKTOP.md](DESKTOP.md) for packaging a branded installer.
