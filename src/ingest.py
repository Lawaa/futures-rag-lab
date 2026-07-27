"""Document ingestion pipeline: load, chunk, embed and persist to ChromaDB."""

from __future__ import annotations

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from .embeddings import build_embeddings
from .logging_config import get_logger
from .manifest import save_manifest
from .settings import Settings

logger = get_logger(__name__)

_TEXT_SUFFIXES = {".txt", ".md"}


def _load_text_file(path: Path) -> list[Document]:
    """Load a plain-text or Markdown file as a single document."""
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return []
    return [Document(page_content=text, metadata={"source": str(path)})]


def _load_pdf_file(path: Path) -> list[Document]:
    """Load a PDF as one document per (non-empty) page.

    Page numbers are stored zero-indexed to match the previous loader's
    metadata, so downstream one-indexed display keeps working.
    """
    reader = PdfReader(str(path))
    documents: list[Document] = []
    for page_number, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if not text.strip():
            continue
        documents.append(
            Document(
                page_content=text,
                metadata={"source": str(path), "page": page_number},
            )
        )
    return documents


def _load_documents(settings: Settings) -> list[Document]:
    """Load every supported document (PDF, TXT, MD) from the data directory."""
    documents: list[Document] = []
    for path in sorted(settings.data_path.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix in _TEXT_SUFFIXES:
            documents.extend(_load_text_file(path))
        elif suffix == ".pdf":
            documents.extend(_load_pdf_file(path))
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