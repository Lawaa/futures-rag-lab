# Automated Code Review & Safety Guard

A local-first pre-commit code quality gate for `futures-rag-lab`. It pairs fast, zero-cost static analysis with optional AI architectural review to catch security vulnerabilities and design smells before code is committed.

---

## 💡 How It Works (2-Tiered Safety Guard & Graph Review)

The system operates in two tiers:

```
[ Git Commit or Manual CLI ]
             │
             ▼
 ┌───────────────────────────────────┐
 │ Tier 1: Instant Local AST Guard   │ ──(Blocking Issue: eval/exec/secrets)──► 🛑 Commit Aborted
 └───────────────────────────────────┘
             │
      (Pass / Warnings)
             │
             ▼
 ┌───────────────────────────────────┐
 │ Tier 2: Code Knowledge Graph      │ ◄─── NetworkX In-Memory Dependency Graph
 │         & AI Impact Review        │      (Traverses IMPORTS, CONTAINS, CALLS)
 └───────────────────────────────────┘
             │ ──(Optional: --llm-review)──► 💬 Cross-File Impact & Design Feedback
             ▼
       ✅ Commit Allowed
```

1. **Tier 1: Fast Local AST Check (Zero-cost, millisecond execution)**
   Uses Python's native Abstract Syntax Tree parser to analyze your code without executing it. It checks for security risks, type annotations, error handling hygiene, and cyclomatic complexity.
   *If a critical safety violation is detected, the check immediately fails and aborts before calling any graph traversal or external APIs.*

2. **Tier 2: Graph-Aware Architectural & Impact Review (Optional with `--llm-review`)**
   Builds an in-memory Code Knowledge Graph (CKG) using `networkx` mapping files, classes, functions, and imports. When a file is modified, it extracts the 1-to-2 hop neighborhood context (upstream callers in other files, downstream calls, and imported modules) and sends this minimal, high-signal context to the configured LLM (Gemini or local Ollama) to identify cross-file breaking changes and architectural side effects.

---

## 🚀 Quickstart

### 1. Install Pre-Commit Git Hook (Recommended)
Automatically run safety checks every time you type `git commit`:
```bash
uv run python -m src.review.cli --install-hook
```
Once installed, any commit containing dangerous constructs like `eval()` or unmasked credentials will be automatically blocked.

### 2. Check Staged Files Manually
Inspect only the files currently staged in Git:
```bash
uv run python -m src.review.cli --staged
```

### 3. Check Specific Files or Folders
```bash
# Check a specific file
uv run python -m src.review.cli --files src/settings.py

# Check multiple directories
uv run python -m src.review.cli --files src/ tests/
```

### 4. Run with AI Architectural Review
Add `--llm-review` to get design critique from your configured LLM (Gemini or local Ollama):
```bash
uv run python -m src.review.cli --staged --llm-review
```

---

## 🛡️ What Gets Checked?

### 🔴 Blocking Security Violations (Stops Commits)
- **Forbidden Execution:** Direct calls to `eval()` or `exec()`.
- **Hardcoded Secrets:** Unmasked credentials or API keys (e.g. AWS access keys, OpenAI/GitHub tokens) assigned directly in source code.

### 🟡 Quality & Maintainability Warnings
- **Type Annotations:** Functions or methods missing parameter type hints or return type annotations.
- **Exception Hygiene:**
  - Bare `except:` clauses that catch everything unconditionally.
  - Silent exception suppression (`except ...: pass`) that hides bugs.
- **Complexity Guard:** Functions with high branching complexity (score > 10) due to nested loops, conditions, or exception handlers.

---

## ⚙️ CLI Options Reference

| Option | Description |
| :--- | :--- |
| `--files [PATH ...]` | One or more Python files or directories to inspect. |
| `--staged` | Inspect only files currently staged for git commit. |
| `--llm-review` | Request second-stage AI architectural & graph impact feedback. |
| `--graph-depth N` | Neighbor traversal depth in the Code Knowledge Graph (default: `2`). |
| `--install-hook` | Write the pre-commit hook into `.git/hooks/pre-commit`. |
| `--complexity-threshold N` | Custom limit for cyclomatic complexity (default: `10`). |
| `--strict` | Fail (exit code 1) on warnings as well as blocking security violations. |

---

## 💻 Working Completely Offline (Ollama)

To use the optional AI reviewer with zero cloud dependencies, configure Ollama in your `.env`:
```env
RAG_LLM_PROVIDER=ollama
RAG_OLLAMA_MODEL=qwen2.5:7b
```
The review system will run entirely on your local machine with full data privacy.
