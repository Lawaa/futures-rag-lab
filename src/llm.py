"""Language-model factory and authentication error helpers."""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

from .credentials import AuthenticationError
from .settings import Settings

_AUTH_ERROR_MARKERS = ("401", "UNAUTHENTICATED", "API_KEY_INVALID", "NOT_FOUND")


def build_llm(settings: Settings, api_key: str | None = None) -> BaseChatModel:
    """Instantiate the chat model for the configured provider.

    - ``gemini``: hosted Google model; requires ``api_key``.
    - ``ollama``: local model served by an Ollama instance; no key needed.
    """
    if settings.llm_provider == "ollama":
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
        )

    if not api_key:
        raise AuthenticationError("A Gemini API key is required for the 'gemini' provider.")

    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=api_key,
    )


def validate_api_key(api_key: str, settings: Settings) -> bool:
    """Return ``True`` if the Gemini API key can perform a trivial invocation."""
    try:
        build_llm(settings, api_key).invoke("ping")
        return True
    except Exception:
        return False


def check_llm_available(settings: Settings, api_key: str | None = None) -> tuple[bool, str | None]:
    """Probe the configured LLM, returning ``(ok, error_message)``.

    Useful for local providers (Ollama) to fail fast with a helpful message
    when the server is down or the model has not been pulled.
    """
    try:
        build_llm(settings, api_key).invoke("ping")
        return True, None
    except Exception as error:
        return False, str(error)


def is_authentication_error(error: Exception) -> bool:
    """Detect authentication/model-not-found errors from the provider."""
    message = str(error)
    return any(marker in message for marker in _AUTH_ERROR_MARKERS)