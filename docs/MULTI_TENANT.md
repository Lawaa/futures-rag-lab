# Multi-Tenant & Multi-Domain RAG Platform

This document describes the multi-tenant and multi-domain architecture of the `futures-rag-lab` platform. It covers tenant isolation, dynamic domain personas, automated compliance guardrails (citation enforcement, PII/PHI scrubbing), API endpoints, and the user interface.

---

## 1. Architecture Overview

The platform extends the base RAG pipeline to serve multiple isolated tenants or distinct domain verticals from a single runtime.

```
+-------------------------------------------------------------------------------+
|                                Frontend Web UI                                |
|  - Profile Switcher ([Default | Legal | Healthcare | Finance])                |
|  - Domain Config Modal (Persona & Guardrails)                                 |
|  - Knowledge Base Manager Modal (Scoped to Tenant)                            |
|  - Embedding Benchmarks Viewer Modal                                          |
+---------------------------------------+---------------------------------------+
                                        | HTTP / SSE
                                        v
+-------------------------------------------------------------------------------+
|                            FastAPI Layer (src/api.py)                         |
|  - GET /profiles, POST /profiles, PUT /profiles/{id}                          |
|  - POST /documents/upload, GET /documents, DELETE /documents/{name}           |
|  - POST /chat, POST /chat/events (with profile_id)                            |
|  - GET /benchmarks/report                                                     |
+---------------------------------------+---------------------------------------+
                                        |
                 +----------------------+----------------------+
                 |                                             |
                 v                                             v
+----------------------------------+          +----------------------------------+
|      Domain Guardrails Engine    |          |    Vector DB / Tenant Isolation  |
|       (src/guardrails.py)        |          |      (src/vector_store.py)       |
|  - PII/PHI Scrubber (SSN, MRN,   |          |  - ChromaDB Collection Naming:   |
|    Email, Phone, Card, DOB)      |          |    "langchain" (Default)         |
|  - Citation Enforcement Injector |          |    "tenant_<id>" (Tenants)       |
|    (Mandatory [Source, Page])    |          |  - Scoped storage: ./data/<id>/  |
+----------------------------------+          +----------------------------------+
                 |                                             |
                 +----------------------+----------------------+
                                        v
+-------------------------------------------------------------------------------+
|                  RAG Service & Retrieval Graph (src/rag_service.py)           |
|  - Cached multi-tenant retrievers (per profile_id)                            |
|  - Contextualized query expansion & routing                                   |
|  - Dynamic answer generation with domain persona & guardrails                 |
+-------------------------------------------------------------------------------+
```

---

## 2. Tenant & Domain Profiles

Profiles configure the assistant's persona, description, and safety guardrails. They are persisted in `profiles.json` at the root of the project.

### Profile Schema

```json
{
  "id": "legal",
  "name": "Legal & Compliance Advisor",
  "description": "Corporate law, contracts, regulatory compliance, and statutory duties.",
  "system_prompt": "You are a senior corporate attorney and regulatory compliance advisor. Provide precise legal interpretations grounded strictly in the provided statutes, case documents, or contract texts.",
  "guardrails": {
    "enforce_citations": true,
    "anonymize_phi": false
  }
}
```

### Supported Built-in Profiles

1. **Default (`default`)**:
   - Focus: General futures trading, margin requirements, settlement, and clearing.
   - Backwards compatible with single-tenant commands (`uv run main.py`).
2. **Legal & Compliance (`legal`)**:
   - Focus: Contractual interpretation, regulatory compliance, and legal frameworks.
   - Guardrails: `enforce_citations = true` (mandates explicit page/document references).
3. **Healthcare & Life Sciences (`healthcare`)**:
   - Focus: Clinical research, protocol guidance, medical data analysis.
   - Guardrails: `anonymize_phi = true` (redacts SSN, MRN, email, phone, card, and DOB).
4. **Quantitative Finance (`finance`)**:
   - Focus: Derivatives valuation, portfolio risk models, VaR calculation, and liquidity analytics.
   - Guardrails: `enforce_citations = true`.

---

## 3. Storage & Vector DB Isolation

### Collection Naming Strategy

To guarantee data segregation across tenants, ChromaDB collection names are partitioned using `get_collection_name(profile_id)`:

- `profile_id == "default"` or `None` $\rightarrow$ Collection `"langchain"` (preserves existing single-tenant databases).
- Any other `profile_id` $\rightarrow$ Collection `"tenant_<sanitized_id>"` (e.g., `tenant_legal`, `tenant_healthcare`).

### Document Storage

- **Default Profile:** Stored in `./data/`
- **Tenant Profiles:** Stored in `./data/<profile_id>/`

When documents are uploaded via `POST /documents/upload?profile_id=<id>`, the file is written to the tenant subfolder and incrementally embedded into that tenant's ChromaDB collection.

---

## 4. Domain Guardrails Engine

The zero-external-dependency guardrail engine in `src/guardrails.py` provides:

### PII & PHI Sanitization (`anonymize_phi: true`)
Automatically redacts sensitive patterns in both user input and generated output:
- **SSN:** `[REDACTED_SSN]`
- **MRN / Patient ID:** `[REDACTED_MRN]`
- **Credit Cards:** `[REDACTED_CARD]`
- **Phone Numbers:** `[REDACTED_PHONE]`
- **Email Addresses:** `[REDACTED_EMAIL]`
- **Dates of Birth:** `[REDACTED_DOB]`

### Citation Enforcement (`enforce_citations: true`)
When enabled, `src/prompts.py` automatically injects mandatory citation constraints into the LLM system prompt:
```
Mandatory Citation Rules:
- Every substantive assertion, finding, or conclusion MUST be explicitly cited with its exact supporting document reference (e.g. '[Source: document, Page: X]').
- Do NOT make uncited claims when deriving answers from context.
```

---

## 5. API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/profiles` | List all available domain profiles and active selection |
| `POST` | `/profiles` | Create a new tenant profile with persona and guardrails |
| `PUT` | `/profiles/{profile_id}` | Update an existing tenant profile |
| `POST` | `/documents/upload` | Upload & index document into active profile collection |
| `GET` | `/documents` | List indexed documents for a profile |
| `DELETE` | `/documents/{filename}` | Delete document and remove from index |
| `GET` | `/documents/{filename}/download` | Download stored document |
| `POST` | `/chat` | Standard question-answering with `profile_id` |
| `POST` | `/chat/events` | SSE streaming chat with status updates and `profile_id` |
| `GET` | `/benchmarks/report` | Fetch latest embedding benchmark results & rankings |

---

## 6. Frontend UI

The web interface (`http://localhost:8000`) includes:
- **Header Profile Switcher:** Dropdown in the top navigation bar to select the active domain profile.
- **Domain Configuration Modal (⚙️ Domain):** Create or edit personas, router descriptions, and toggle guardrail rules.
- **Knowledge Base Manager Modal (📁 Docs):** Upload, index, inspect, and delete documents for the active profile.
- **Embedding Benchmarks Modal (📊 Benchmarks):** View real-time benchmark summaries, composite scores, and top 3 winner rankings.
