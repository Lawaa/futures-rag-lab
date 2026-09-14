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
from .vector_store import get_collection_name

logger = get_logger(__name__)

_TEXT_SUFFIXES = {".txt", ".md"}


def _load_text_file(path: Path) -> list[Document]:
    """Load a plain-text or Markdown file as a single document."""
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return []
    return [Document(page_content=text, metadata={"source": str(path)})]


def _load_pdf_file(path: Path) -> list[Document]:
    """Load a PDF as one document per (non-empty) page."""
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


def _load_documents(data_path: Path) -> list[Document]:
    """Load every supported document (PDF, TXT, MD) from a directory."""
    documents: list[Document] = []
    for path in sorted(data_path.rglob("*")):
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


def ingest_file_to_vector_db(
    file_path: Path, settings: Settings, profile_id: str | None = None
) -> int:
    """Ingest a single document into the appropriate tenant vector store collection."""
    suffix = file_path.suffix.lower()
    if suffix in _TEXT_SUFFIXES:
        docs = _load_text_file(file_path)
    elif suffix == ".pdf":
        docs = _load_pdf_file(file_path)
    else:
        return 0

    if not docs:
        return 0

    chunks = _split_documents(docs, settings)
    collection_name = get_collection_name(profile_id)
    Chroma.from_documents(
        documents=chunks,
        embedding=build_embeddings(settings),
        persist_directory=str(settings.db_path),
        collection_name=collection_name,
    )
    logger.info("Ingested %d chunks from '%s' into collection '%s'.", len(chunks), file_path.name, collection_name)
    return len(chunks)


def build_vector_db(settings: Settings, profile_id: str | None = None) -> bool:
    """Ingest documents into ChromaDB for a given profile or the default workspace."""
    data_dir = settings.data_path
    if profile_id and profile_id != "default":
        data_dir = settings.data_path / profile_id

    if not data_dir.exists() or not any(data_dir.iterdir()):
        logger.warning("Data directory '%s' is empty or missing.", data_dir)
        return False

    logger.info("Loading documents (PDF, TXT, MD) from '%s'...", data_dir)
    documents = _load_documents(data_dir)
    logger.info("Loaded %d document source pages/files.", len(documents))

    if not documents:
        logger.warning("No supported documents found in '%s'.", data_dir)
        return False

    chunks = _split_documents(documents, settings)
    logger.info("Created %d text chunks.", len(chunks))

    collection_name = get_collection_name(profile_id)
    logger.info(
        "Generating embeddings with '%s' and persisting to ChromaDB collection '%s'...",
        settings.embedding_model,
        collection_name,
    )
    Chroma.from_documents(
        documents=chunks,
        embedding=build_embeddings(settings),
        persist_directory=str(settings.db_path),
        collection_name=collection_name,
    )

    if not profile_id or profile_id == "default":
        save_manifest(settings)
    logger.info("Successfully indexed %d chunks into '%s' (collection: %s).", len(chunks), settings.db_path, collection_name)
    return True