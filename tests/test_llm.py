"""Tests for the provider-aware LLM factory."""

from __future__ import annotations

import pytest
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

from src.credentials import AuthenticationError
from src.llm import build_llm, is_authentication_error
from src.settings import Settings


def test_build_llm_ollama_needs_no_key() -> None:
    settings = Settings(llm_provider="ollama", ollama_model="qwen2.5:7b")
    llm = build_llm(settings)
    assert isinstance(llm, ChatOllama)
    assert llm.model == "qwen2.5:7b"


def test_build_llm_gemini_requires_key() -> None:
    settings = Settings(llm_provider="gemini")
    with pytest.raises(AuthenticationError):
        build_llm(settings)


def test_build_llm_gemini_with_key() -> None:
    settings = Settings(llm_provider="gemini", gemini_model="gemini-x")
    llm = build_llm(settings, api_key="dummy")
    assert isinstance(llm, ChatGoogleGenerativeAI)


def test_is_authentication_error() -> None:
    assert is_authentication_error(Exception("API_KEY_INVALID")) is True
    assert is_authentication_error(Exception("connection refused")) is False