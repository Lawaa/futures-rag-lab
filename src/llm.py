"""Language-model factory and authentication error helpers."""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

from .credentials import AuthenticationError
from .settings import Settings

_AUTH_ERROR_MARKERS = ("401", "UNAUTHENTICATED", "API_KEY_INVALID", "NOT_FOUND")


def _build_rate_limiter(settings: Settings) -> InMemoryRateLimiter | None:
    """Create a shared client-side rate limiter, or ``None`` when disabled.

    A single limiter instance is attached to the model so every LLM call in the
    LangGraph pipeline (query prep, grading, rewriting, generation) draws from
    the same budget and stays under provider quotas.
    """
    rpm = settings.llm_requests_per_minute
    if rpm <= 0:
        return None
    return InMemoryRateLimiter(
        requests_per_second=rpm / 60.0,
        check_every_n_seconds=0.1,
        max_bucket_size=float(max(1, rpm)),
    )


def build_llm(settings: Settings, api_key: str | None = None) -> BaseChatModel:
    """Instantiate the chat model for the configured provider.

    - ``gemini``: hosted Google model; requires ``api_key``.
    - ``ollama``: local model served by an Ollama instance; no key needed.
    """
    rate_limiter = _build_rate_limiter(settings)

    if settings.llm_provider == "ollama":
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            rate_limiter=rate_limiter,
        )

    if not api_key:
        raise AuthenticationError("A Gemini API key is required for the 'gemini' provider.")

    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=api_key,
        rate_limiter=rate_limiter,
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
        import traceback
        traceback.print_exc()  # full detail to server console/logs only
        if is_authentication_error(error):
            return False, "Invalid or missing API key."
        return False, "The language model is currently unavailable."

def is_authentication_error(error: Exception) -> bool:
    """Detect authentication/model-not-found errors from the provider."""
    message = str(error)
    return any(marker in message for marker in _AUTH_ERROR_MARKERS)