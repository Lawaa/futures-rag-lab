"""ChromaDB vector store and retriever factories."""

from __future__ import annotations

from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever

from .embeddings import build_embeddings
from .settings import Settings


def build_vector_store(settings: Settings) -> Chroma:
    """Open (or create) the persistent Chroma vector store."""
    return Chroma(
        persist_directory=str(settings.db_path),
        embedding_function=build_embeddings(settings),
    )


def build_retriever(settings: Settings) -> VectorStoreRetriever:
    """Build a Maximum Marginal Relevance retriever for balanced coverage."""
    return build_vector_store(settings).as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": settings.retriever_k,
            "fetch_k": settings.retriever_fetch_k,
            "lambda_mult": settings.retriever_lambda_mult,
        },
    )