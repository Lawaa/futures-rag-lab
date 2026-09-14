"""Synthetic dataset generation for embedding model benchmarking.

Generates Question-Context-Answer (QCA) evaluation pairs from domain documents
using the configured LLM and deterministic chunk identification.
"""

from __future__ import annotations

import json
import random
import re
import time
from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from ..credentials import get_stored_api_key
from ..ingest import _load_documents, _split_documents
from ..llm import build_llm
from ..logging_config import get_logger
from ..settings import Settings, get_settings

logger = get_logger(__name__)


class BenchmarkItem(BaseModel):
    """Single benchmark evaluation test item."""

    query: str = Field(..., description="Evaluation search query or question.")
    expected_doc_id: str = Field(..., description="Deterministic unique identifier of the target chunk.")
    expected_chunk_text: str = Field(..., description="Text content of the expected target chunk.")
    answer: str | None = Field(default=None, description="Synthetic ground-truth answer.")
    source_file: str | None = Field(default=None, description="Origin filename or path.")


class BenchmarkDataset(BaseModel):
    """Collection of benchmark evaluation items."""

    items: list[BenchmarkItem] = Field(default_factory=list)

    def save(self, path: Path | str) -> None:
        """Persist the dataset to a JSON file."""
        target_path = Path(path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(self.model_dump_json(indent=2), encoding="utf-8")
        logger.info("Persisted benchmark dataset with %d items to %s", len(self.items), target_path)

    @classmethod
    def load(cls, path: Path | str) -> BenchmarkDataset:
        """Load a benchmark dataset from a JSON file."""
        target_path = Path(path)
        if not target_path.exists():
            raise FileNotFoundError(f"Benchmark dataset not found at {target_path}")
        raw_data = json.loads(target_path.read_text(encoding="utf-8"))
        return cls.model_validate(raw_data)


def assign_chunk_ids(chunks: list[Document]) -> list[Document]:
    """Assign deterministic IDs to document chunks."""
    for idx, chunk in enumerate(chunks):
        source = chunk.metadata.get("source", "doc")
        source_name = Path(source).name
        page = chunk.metadata.get("page", 0)
        chunk_id = f"{source_name}:p{page}:c{idx}"
        chunk.metadata["doc_id"] = chunk_id
    return chunks


_SYNTHETIC_PROMPT_TEMPLATE = """You are an expert domain evaluator creating benchmark test data for an information retrieval system.
Given the following excerpt from a domain document, generate:
1. A specific, natural domain question or search query that is directly answered by this excerpt.
2. A concise, factual answer based strictly on the excerpt.

Excerpt:
\"\"\"{context}\"\"\"

Respond STRICTLY with a valid JSON object in this format:
{{
  "query": "Your generated search question or query here",
  "answer": "Concise answer here"
}}
"""


class SyntheticDatasetGenerator:
    """Generates synthetic QCA benchmark datasets using ingested documents and an LLM."""

    def __init__(
        self,
        settings: Settings | None = None,
        llm: BaseChatModel | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self._llm = llm

    @property
    def llm(self) -> BaseChatModel:
        """Lazily initialize the configured chat model."""
        if self._llm is None:
            api_key = get_stored_api_key() if self.settings.uses_gemini else None
            self._llm = build_llm(self.settings, api_key=api_key)
        return self._llm

    def load_and_chunk_documents(self) -> list[Document]:
        """Load domain documents and split into chunks with deterministic IDs."""
        documents = _load_documents(self.settings)
        if not documents:
            raise RuntimeError(f"No documents found in data directory: {self.settings.data_path}")
        chunks = _split_documents(documents, self.settings)
        return assign_chunk_ids(chunks)

    def generate_item_from_chunk(self, chunk: Document) -> BenchmarkItem | None:
        """Generate a single BenchmarkItem from a document chunk using LLM."""
        context = chunk.page_content.strip()
        if len(context) < 80:
            return None

        prompt = _SYNTHETIC_PROMPT_TEMPLATE.format(context=context[:1500])
        response = self.llm.invoke(
            [
                SystemMessage(content="You generate realistic evaluation queries for search systems in JSON."),
                HumanMessage(content=prompt),
            ]
        )
        content = response.content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict) and "text" in item:
                    parts.append(str(item["text"]))
                elif hasattr(item, "text"):
                    parts.append(str(item.text))
                else:
                    parts.append(str(item))
            content = "\n".join(parts)
        elif not isinstance(content, str):
            content = str(content)

        # Extract JSON from potential markdown fences
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if not json_match:
            logger.warning("Failed to extract JSON from LLM response for chunk %s", chunk.metadata.get("doc_id"))
            return None

        try:
            parsed = json.loads(json_match.group(0))
            query = parsed.get("query", "").strip()
            answer = parsed.get("answer", "").strip()
            if not query:
                return None

            doc_id = chunk.metadata.get("doc_id", "unknown")
            source = chunk.metadata.get("source")
            return BenchmarkItem(
                query=query,
                expected_doc_id=doc_id,
                expected_chunk_text=chunk.page_content,
                answer=answer,
                source_file=Path(source).name if source else None,
            )
        except Exception as err:
            logger.warning("Error parsing LLM response for chunk: %s", err)
            return None

    def generate(
        self,
        num_samples: int = 15,
        save_path: Path | str | None = None,
        seed: int = 42,
    ) -> BenchmarkDataset:
        """Generate a benchmark dataset of target size and optionally persist it."""
        chunks = self.load_and_chunk_documents()
        logger.info("Loaded %d chunks for synthetic benchmark generation.", len(chunks))

        # Ensure chunks have sufficient content length
        eligible_chunks = [c for c in chunks if len(c.page_content.strip()) >= 100]
        if not eligible_chunks:
            eligible_chunks = chunks

        # Sample evenly across chunks
        rng = random.Random(seed)
        sample_pool = eligible_chunks.copy()
        rng.shuffle(sample_pool)

        items: list[BenchmarkItem] = []
        for chunk in sample_pool:
            if len(items) >= num_samples:
                break
            try:
                item = self.generate_item_from_chunk(chunk)
                if item:
                    items.append(item)
                    logger.info("Generated benchmark item %d/%d: '%s'", len(items), num_samples, item.query)
                # Polite delay to respect API rate limits
                time.sleep(1.0)
            except Exception as err:
                logger.warning("Skipping chunk due to generation error: %s", err)
                time.sleep(2.0)

        dataset = BenchmarkDataset(items=items)
        if save_path:
            dataset.save(save_path)
        return dataset
