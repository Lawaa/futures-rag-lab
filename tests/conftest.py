"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.settings import Settings


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    """Settings pointing at isolated temporary directories."""
    return Settings(data_path=tmp_path / "data", db_path=tmp_path / "chroma_db")