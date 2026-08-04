"""Centralized application configuration.

All tunable parameters live here and can be overridden through environment
variables (prefixed with ``RAG_``) or a local ``.env`` file, keeping the rest of
the codebase free of magic constants.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed, validated application settings."""

    model_config = SettingsConfigDict(
        env_prefix="RAG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Storage paths -------------------------------------------------------
    data_path: Path = Field(default=Path("./data"), description="Source documents directory.")
    db_path: Path = Field(default=Path("./chroma_db"), description="ChromaDB persistence directory.")

    # --- Embeddings ----------------------------------------------------------
    embedding_model: str = Field(default="BAAI/bge-small-en-v1.5")

    # --- Interface language --------------------------------------------------
    # Language used for assistant answers and the user interface (CLI/Web).
    language: Literal["en", "hu"] = Field(default="en")

    # --- Language model ------------------------------------------------------
    # Choose the backend: hosted Google Gemini or a local Ollama server.
    llm_provider: Literal["gemini", "ollama"] = Field(default="gemini")
    gemini_model: str = Field(default="gemini-3.5-flash-lite")
    ollama_model: str = Field(default="qwen2.5:7b")
    ollama_base_url: str = Field(default="http://localhost:11434")

    # --- Rate limiting -------------------------------------------------------
    # Optional client-side throttle shared by every LLM call to stay under
    # provider quotas (e.g. Gemini free-tier RPM). 0 disables throttling.
    llm_requests_per_minute: int = Field(default=0, ge=0)

    # --- Chunking ------------------------------------------------------------
    chunk_size: int = Field(default=1200, gt=0)
    chunk_overlap: int = Field(default=200, ge=0)

    # --- Retrieval (Maximum Marginal Relevance) ------------------------------
    retriever_k: int = Field(default=6, gt=0, description="Number of documents returned.")
    retriever_fetch_k: int = Field(default=20, gt=0, description="Candidate pool size for MMR.")
    retriever_lambda_mult: float = Field(default=0.7, ge=0.0, le=1.0)

    # --- Cross-lingual retrieval & self-correction ---------------------------
    # Search queries are always translated into this corpus language so a
    # question asked in any language can still match the stored documents.
    retrieval_language: Literal["en", "hu"] = Field(default="en")
    # When enabled, retrieved documents are graded for relevance and the query
    # is rewritten (up to ``max_retrieval_retries`` times) if they are not.
    enable_self_correction: bool = Field(default=True)
    max_retrieval_retries: int = Field(
        default=3, ge=0, description="Max query rewrites when documents are irrelevant."
    )
    # After generation, verify the answer is grounded in the retrieved context
    # (Self-RAG / CRAG). Ungrounded answers are labelled and lose their (false)
    # local-document citations.
    enable_groundedness_check: bool = Field(default=True)

    # --- Multi-query retrieval (fan-out + reranking) -------------------------
    # Generate several query variants, retrieve for each in parallel and fuse the
    # ranked lists with Reciprocal Rank Fusion for broader, more robust recall.
    enable_multi_query: bool = Field(default=False)
    multi_query_count: int = Field(
        default=3, ge=1, le=8, description="Number of query variants to fan out to."
    )

    # --- Durable graph state -------------------------------------------------
    # Persist the retrieval graph's per-conversation state with a LangGraph
    # SQLite checkpointer so turns are durable and resumable across restarts.
    enable_checkpointing: bool = Field(default=True)

    # --- Multi-business profiles / tenant routing ----------------------------
    # Optional JSON file defining named profiles (persona + system prompt) so a
    # single build can serve different businesses. Absent file => one default.
    profiles_path: Path = Field(default=Path("./profiles.json"))
    # Active profile for this deployment (used when routing is off).
    profile: str = Field(default="default")
    # When on and multiple profiles exist, classify each question and route it
    # to the best-matching profile's system prompt.
    enable_profile_routing: bool = Field(default=False)

    # --- API server ----------------------------------------------------------
    api_host: str = Field(default="127.0.0.1")
    api_port: int = Field(default=8000, gt=0, le=65535)

    # --- AWS S3 Storage (Optional) -------------------------------------------
    use_s3_storage: bool = Field(default=False, description="Enable S3 document storage.")
    aws_access_key_id: str | None = Field(default=None, description="AWS access key ID.")
    aws_secret_access_key: str | None = Field(default=None, description="AWS secret access key.")
    aws_region: str = Field(default="eu-central-1", description="AWS region.")
    aws_s3_bucket_name: str = Field(default="futures-rag-lab-docs", description="S3 bucket name.")

    @property
    def manifest_path(self) -> Path:
        """Location of the ingestion fingerprint manifest."""
        return self.db_path / ".data_manifest.json"

    @property
    def conversations_db_path(self) -> Path:
        """Location of the persistent conversation history database."""
        return self.db_path / "conversations.sqlite3"

    @property
    def graph_checkpoint_path(self) -> Path:
        """Location of the LangGraph SQLite checkpoint database."""
        return self.db_path / "graph_checkpoints.sqlite3"

    @property
    def uses_gemini(self) -> bool:
        """Whether the hosted Gemini backend (and thus an API key) is in use."""
        return self.llm_provider == "gemini"

    @property
    def is_hungarian(self) -> bool:
        """Whether the interface and answers should be in Hungarian."""
        return self.language == "hu"

    @property
    def active_model(self) -> str:
        """Human-readable name of the model that will handle requests."""
        return self.gemini_model if self.uses_gemini else self.ollama_model


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached, process-wide :class:`Settings` instance."""
    return Settings()