"""Embedding-model factory.

Uses Qdrant FastEmbed (ONNX Runtime) so the desktop sidecar does not need to
ship PyTorch / sentence-transformers — the main reason installers were hundreds
of megabytes. Models are downloaded into the user cache on first use, not baked
into the installer.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from langchain_core.embeddings import Embeddings

from .settings import Settings


class FastEmbedEmbeddings(Embeddings):
    """Thin LangChain adapter around ``fastembed.TextEmbedding``."""

    def __init__(self, model_name: str) -> None:
        from fastembed import TextEmbedding

        self._model = TextEmbedding(model_name=model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [_as_float_list(vector) for vector in self._model.embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        return next(iter(self.embed_documents([text])))


def _as_float_list(vector: Any) -> list[float]:
    if hasattr(vector, "tolist"):
        return [float(x) for x in vector.tolist()]
    return [float(x) for x in vector]


@lru_cache(maxsize=4)
def _cached_embeddings(model_name: str) -> Embeddings:
    return FastEmbedEmbeddings(model_name=model_name)


def build_embeddings(settings: Settings) -> Embeddings:
    """Return a cached embedding model for the configured model name."""
    return _cached_embeddings(settings.embedding_model)
