"""Tests for the bundled desktop backend entry point."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ENTRY_PATH = REPO_ROOT / "desktop" / "backend" / "entry.py"


def _load_entry():
    spec = importlib.util.spec_from_file_location("desktop_entry", ENTRY_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_user_data_root_follows_platform_conventions(monkeypatch) -> None:
    entry = _load_entry()
    monkeypatch.setenv("HOME", "/home/tester")
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.setattr(entry.sys, "platform", "linux")

    assert entry.user_data_root() == Path(
        "/home/tester/.local/share/FuturesTradingAssistant"
    )


def test_configure_environment_points_settings_at_user_dirs(
    tmp_path, monkeypatch
) -> None:
    entry = _load_entry()
    monkeypatch.setattr(entry, "user_data_root", lambda: tmp_path)
    for var in ("RAG_DATA_PATH", "RAG_DB_PATH", "RAG_API_HOST", "RAG_API_PORT"):
        monkeypatch.delenv(var, raising=False)

    host, port = entry.configure_environment()

    assert host == "127.0.0.1"
    assert port == 8000
    assert os.environ["RAG_DATA_PATH"] == str(tmp_path / "data")
    assert os.environ["RAG_DB_PATH"] == str(tmp_path / "chroma_db")
    assert (tmp_path / "chroma_db").is_dir()
    # The default starter documents were seeded into the empty data directory.
    assert any((tmp_path / "data").iterdir())


def test_seed_does_not_overwrite_existing_documents(tmp_path) -> None:
    entry = _load_entry()
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "my-notes.txt").write_text("private", encoding="utf-8")

    entry._seed_default_documents(data_dir)

    assert (data_dir / "my-notes.txt").read_text(encoding="utf-8") == "private"
    # Seeding is skipped entirely when the folder already has content.
    assert not (data_dir / "trading-glossary.txt").exists()
