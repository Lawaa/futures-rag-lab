"""Embedding-model factory."""

from __future__ import annotations

from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from .settings import Settings


@lru_cache(maxsize=4)
def _cached_embeddings(model_name: str) -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=model_name)


def build_embeddings(settings: Settings) -> HuggingFaceEmbeddings:
    """Return a cached embedding model for the configured model name."""
    return _cached_embeddings(settings.embedding_model)