# Automated Code Review & Safety Guard

A local-first pre-commit code quality gate for `futures-rag-lab`. It pairs fast, zero-cost static analysis with optional AI architectural review to catch security vulnerabilities and design smells before code is committed.

---

## 💡 How It Works

The system operates in two stages:

```
[ Git Commit or Manual CLI ]
             │
             ▼
 ┌───────────────────────┐
 │ Stage 1: AST Analyzer │ ──(Blocking Issue: eval/exec/secrets)──► 🛑 Commit Aborted
 └───────────────────────┘
             │
      (Pass / Warnings)
             │
             ▼
 ┌───────────────────────┐
 │ Stage 2: AI Reviewer  │ ──(Optional: --llm-review)─────────────► 💬 Design Feedback
 └───────────────────────┘
             │
             ▼
         ✅ Commit Allowed
```

1. **Stage 1: Fast Local AST Check (Zero-cost, millisecond execution)**
   Uses Python's native Abstract Syntax Tree parser to analyze your code without executing it. It checks for security risks, type annotations, error handling hygiene, and cyclomatic complexity.
   *If a critical safety violation is detected, the check immediately fails and aborts before calling any external APIs.*

2. **Stage 2: AI Architectural Review (Optional)**
   If enabled, a condensed structural summary of your code is sent to your configured language model (hosted Gemini or local Ollama) to give actionable feedback on modularity, error resilience, and code clarity.

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
| `--llm-review` | Request second-stage AI architectural feedback. |
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
