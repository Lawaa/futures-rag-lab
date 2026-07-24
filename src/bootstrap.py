"""Application bootstrap: database preparation and service assembly.

Shared by every interface (CLI, API) so wiring lives in exactly one place.
"""

from __future__ import annotations

import shutil

from .ingest import build_vector_db
from .llm import build_llm
from .logging_config import get_logger
from .manifest import is_data_changed
from .rag_service import RagService
from .settings import Settings
from .vector_store import build_retriever


logger = get_logger(__name__)


def ensure_vector_db(settings: Settings) -> bool:
    """Ensure the vector store exists and reflects the current data directory.

    Returns ``True`` if a usable database is available afterwards.
    """
    db_exists = settings.db_path.exists() and any(settings.db_path.iterdir())
    data_changed = is_data_changed(settings)

    if db_exists and not data_changed:
        logger.info("Vector database up to date.")
        return True

    if db_exists and data_changed:
        logger.info("Data directory changed; rebuilding vector database.")
        shutil.rmtree(settings.db_path, ignore_errors=True)
    else:
        logger.info("Vector database not found; building it now.")

    return build_vector_db(settings)


def build_service(settings: Settings, api_key: str | None = None) -> RagService:
    """Assemble a :class:`RagService`, rebuilding on embedding mismatches."""
    llm = build_llm(settings, api_key)
    try:
        retriever = build_retriever(settings)
    except Exception as error:  # pragma: no cover - defensive rebuild path
        message = str(error).lower()
        if "dimension" not in message and "embedding" not in message:
            raise
        logger.warning("Embedding mismatch detected; rebuilding vector database.")
        shutil.rmtree(settings.db_path, ignore_errors=True)
        if not build_vector_db(settings):
            raise
        retriever = build_retriever(settings)

    return RagService(llm=llm, retriever=retriever, settings=settings)