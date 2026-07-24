"""Application-wide logging configuration."""

from __future__ import annotations

import logging

_CONFIGURED = False


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logging once with a concise, readable format."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    _CONFIGURED = True


def set_log_level(level: int) -> None:
    """Adjust the active root log level (e.g. to quiet a CLI session)."""
    configure_logging()
    logging.getLogger().setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger, ensuring logging is configured."""
    configure_logging()
    return logging.getLogger(name)