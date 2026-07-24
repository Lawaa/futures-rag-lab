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

    # --- Language model ------------------------------------------------------
    # Choose the backend: hosted Google Gemini or a local Ollama server.
    llm_provider: Literal["gemini", "ollama"] = Field(default="gemini")
    gemini_model: str = Field(default="gemini-3.5-flash-lite")
    ollama_model: str = Field(default="qwen2.5:7b")
    ollama_base_url: str = Field(default="http://localhost:11434")

    # --- Chunking ------------------------------------------------------------
    chunk_size: int = Field(default=1200, gt=0)
    chunk_overlap: int = Field(default=200, ge=0)

    # --- Retrieval (Maximum Marginal Relevance) ------------------------------
    retriever_k: int = Field(default=6, gt=0, description="Number of documents returned.")
    retriever_fetch_k: int = Field(default=20, gt=0, description="Candidate pool size for MMR.")
    retriever_lambda_mult: float = Field(default=0.7, ge=0.0, le=1.0)

    # --- API server ----------------------------------------------------------
    api_host: str = Field(default="127.0.0.1")
    api_port: int = Field(default=8000, gt=0, le=65535)

    @property
    def manifest_path(self) -> Path:
        """Location of the ingestion fingerprint manifest."""
        return self.db_path / ".data_manifest.json"

    @property
    def uses_gemini(self) -> bool:
        """Whether the hosted Gemini backend (and thus an API key) is in use."""
        return self.llm_provider == "gemini"

    @property
    def active_model(self) -> str:
        """Human-readable name of the model that will handle requests."""
        return self.gemini_model if self.uses_gemini else self.ollama_model


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached, process-wide :class:`Settings` instance."""
    return Settings()