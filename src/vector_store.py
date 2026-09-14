"""ChromaDB vector store and retriever factories."""

from __future__ import annotations

import re

from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever

from .embeddings import build_embeddings
from .settings import Settings

DEFAULT_COLLECTION_NAME = "langchain"


def get_collection_name(profile_id: str | None = None) -> str:
    """Return collection name scoped to profile_id, preserving default backwards compatibility."""
    if not profile_id or profile_id == "default":
        return DEFAULT_COLLECTION_NAME
    clean_id = re.sub(r"[^a-zA-Z0-9_-]", "_", profile_id.strip().lower())
    return f"tenant_{clean_id}"


def build_vector_store(settings: Settings, profile_id: str | None = None) -> Chroma:
    """Open (or create) the persistent Chroma vector store for a specific profile/tenant."""
    return Chroma(
        persist_directory=str(settings.db_path),
        embedding_function=build_embeddings(settings),
        collection_name=get_collection_name(profile_id),
    )


def build_retriever(settings: Settings, profile_id: str | None = None) -> VectorStoreRetriever:
    """Build a Maximum Marginal Relevance retriever for balanced coverage for a tenant."""
    return build_vector_store(settings, profile_id=profile_id).as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": settings.retriever_k,
            "fetch_k": settings.retriever_fetch_k,
            "lambda_mult": settings.retriever_lambda_mult,
        },
    )