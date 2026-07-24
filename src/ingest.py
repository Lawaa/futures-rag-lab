"""Document ingestion pipeline: load, chunk, embed and persist to ChromaDB."""

from __future__ import annotations

from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .embeddings import build_embeddings
from .logging_config import get_logger
from .manifest import save_manifest
from .settings import Settings

logger = get_logger(__name__)


def _load_documents(settings: Settings) -> list[Document]:
    """Load every supported document (PDF, TXT, MD) from the data directory."""
    text_kwargs = {"encoding": "utf-8"}
    loaders = [
        DirectoryLoader(str(settings.data_path), glob="**/*.pdf", loader_cls=PyPDFLoader),
        DirectoryLoader(
            str(settings.data_path), glob="**/*.txt", loader_cls=TextLoader, loader_kwargs=text_kwargs
        ),
        DirectoryLoader(
            str(settings.data_path), glob="**/*.md", loader_cls=TextLoader, loader_kwargs=text_kwargs
        ),
    ]

    documents: list[Document] = []
    for loader in loaders:
        documents.extend(loader.load())
    return documents


def _split_documents(documents: list[Document], settings: Settings) -> list[Document]:
    """Split documents into overlapping chunks for retrieval."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    return splitter.split_documents(documents)


def build_vector_db(settings: Settings) -> bool:
    """Ingest the data directory into ChromaDB.

    Returns ``True`` on success, ``False`` when there is nothing to ingest.
    """
    if not settings.data_path.exists() or not any(settings.data_path.iterdir()):
        logger.warning("Data directory '%s' is empty or missing.", settings.data_path)
        return False

    logger.info("Loading documents (PDF, TXT, MD) from '%s'...", settings.data_path)
    documents = _load_documents(settings)
    logger.info("Loaded %d document source pages/files.", len(documents))

    if not documents:
        logger.warning("No supported documents found in '%s'.", settings.data_path)
        return False

    chunks = _split_documents(documents, settings)
    logger.info("Created %d text chunks.", len(chunks))

    logger.info(
        "Generating embeddings with '%s' and persisting to ChromaDB...",
        settings.embedding_model,
    )
    Chroma.from_documents(
        documents=chunks,
        embedding=build_embeddings(settings),
        persist_directory=str(settings.db_path),
    )

    save_manifest(settings)
    logger.info("Successfully indexed %d chunks into '%s'.", len(chunks), settings.db_path)
    return True