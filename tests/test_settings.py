from __future__ import annotations

from pathlib import Path

from src.settings import Settings


def test_defaults() -> None:
    settings = Settings()
    assert settings.embedding_model == "BAAI/bge-small-en-v1.5"
    assert settings.retriever_k == 6
    assert 0.0 <= settings.retriever_lambda_mult <= 1.0
    assert settings.llm_provider == "gemini"
    assert settings.uses_gemini is True
    assert settings.active_model == settings.gemini_model


def test_manifest_path_derives_from_db_path() -> None:
    settings = Settings(db_path=Path("/tmp/db"))
    assert settings.manifest_path == Path("/tmp/db/.data_manifest.json")


def test_env_override(monkeypatch) -> None:
    monkeypatch.setenv("RAG_GEMINI_MODEL", "custom-model")
    monkeypatch.setenv("RAG_RETRIEVER_K", "9")
    settings = Settings()
    assert settings.gemini_model == "custom-model"
    assert settings.retriever_k == 9


def test_ollama_provider_selection(monkeypatch) -> None:
    monkeypatch.setenv("RAG_LLM_PROVIDER", "ollama")
    monkeypatch.setenv("RAG_OLLAMA_MODEL", "qwen2.5:7b")
    settings = Settings()
    assert settings.llm_provider == "ollama"
    assert settings.uses_gemini is False
    assert settings.active_model == "qwen2.5:7b"