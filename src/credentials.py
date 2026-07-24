"""Secure Gemini API-key management via the OS-native credential store."""

from __future__ import annotations

import os

import keyring

from .logging_config import get_logger

logger = get_logger(__name__)

SERVICE_NAME = "futures-rag-lab"
KEY_NAME = "GEMINI_API_KEY"


class AuthenticationError(RuntimeError):
    """Raised when a valid API key cannot be obtained."""


def get_stored_api_key() -> str | None:
    """Return the API key from the environment or the system keyring."""
    env_key = os.getenv("GEMINI_API_KEY")
    if env_key:
        return env_key
    return keyring.get_password(SERVICE_NAME, KEY_NAME)


def store_api_key(api_key: str) -> None:
    """Persist an API key to the system credential store."""
    keyring.set_password(SERVICE_NAME, KEY_NAME, api_key)


def delete_stored_api_key() -> None:
    """Delete the stored API key, ignoring the case where none exists."""
    try:
        keyring.delete_password(SERVICE_NAME, KEY_NAME)
        logger.info("Stored API key removed from system credential storage.")
    except keyring.errors.PasswordDeleteError:
        pass