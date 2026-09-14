"""Tests for the dynamic legal corpus downloader and caching module."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import urllib.error

import pytest

from src.legal_fetcher import LEGAL_CORPORA, LegalCorpusManager, MIN_LEGAL_FILE_SIZE
from src.settings import get_settings


def _create_mock_legal_bytes(size: int = MIN_LEGAL_FILE_SIZE + 1024) -> bytes:
    """Helper to create dummy valid legal statutory bytes exceeding threshold."""
    header = "2013. évi V. törvény a Polgári Törvénykönyvről (Ptk.)\n1:1. § [Hatály]\n"
    padding = "Jogszabályi rendelkezés és kötelmi jogi tartalom. " * (size // 45)
    return (header + padding).encode("utf-8")


@pytest.fixture
def temp_legal_mgr(tmp_path: Path) -> LegalCorpusManager:
    """Create a LegalCorpusManager with an isolated data directory."""
    settings = get_settings().model_copy(update={"data_path": tmp_path})
    return LegalCorpusManager(settings=settings)


def test_legal_corpus_manager_init(temp_legal_mgr: LegalCorpusManager, tmp_path: Path) -> None:
    """Verify initialization and legal dir creation."""
    assert temp_legal_mgr.legal_dir == tmp_path / "legal"
    assert temp_legal_mgr.legal_dir.exists()
    assert temp_legal_mgr.legal_dir.is_dir()


def test_get_available_corpora_initially_empty(temp_legal_mgr: LegalCorpusManager) -> None:
    """Verify corpora list when no files are cached yet."""
    corpora = temp_legal_mgr.get_available_corpora()
    assert len(corpora) == len(LEGAL_CORPORA)
    for c in corpora:
        assert c["id"] in ("ptk", "btk")
        assert c["status"] == "available"
        assert c["size_bytes"] == 0
        assert c["is_active"] is False
        assert c["last_synced"] is None


def test_check_and_sync_corpus_unknown(temp_legal_mgr: LegalCorpusManager) -> None:
    """Verify error raised on unknown corpus ID."""
    with pytest.raises(ValueError, match="Unknown legal corpus ID"):
        temp_legal_mgr.check_and_sync_corpus("nonexistent_code")


def test_check_and_sync_corpus_size_too_small_raises(
    temp_legal_mgr: LegalCorpusManager, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that downloads under 100 KB raise an explicit RuntimeError."""
    stub_bytes = b"2013. evi V. torveny 1:1. paragrafus small text stub"
    monkeypatch.setattr(
        temp_legal_mgr, "_fetch_content", lambda url, cid: (stub_bytes, None, None)
    )
    # The _validate_legal_content will fail or _fetch_content raises
    with pytest.raises(RuntimeError, match="too small"):
        from src.legal_fetcher import _validate_legal_content
        _validate_legal_content(stub_bytes, "ptk")


def test_check_and_sync_corpus_first_download_file(
    temp_legal_mgr: LegalCorpusManager, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify first sync creates legal text file when content is valid."""
    mock_bytes = _create_mock_legal_bytes()
    monkeypatch.setattr(
        temp_legal_mgr, "_fetch_content", lambda url, cid: (mock_bytes, "etag1", None)
    )
    monkeypatch.setattr("src.legal_fetcher.ingest_file_to_vector_db", MagicMock(return_value=5))

    file_path = temp_legal_mgr.check_and_sync_corpus("ptk")

    assert file_path.exists()
    assert file_path.name == "ptk_2013_v.txt"
    assert "Polgári Törvénykönyvről" in file_path.read_text(encoding="utf-8")
    assert file_path.stat().st_size >= MIN_LEGAL_FILE_SIZE


def test_check_and_sync_corpus_first_download_manifest(
    temp_legal_mgr: LegalCorpusManager, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify manifest is updated and vector DB ingestion is invoked."""
    mock_bytes = _create_mock_legal_bytes()
    monkeypatch.setattr(
        temp_legal_mgr, "_fetch_content", lambda url, cid: (mock_bytes, "etag1", None)
    )
    ingest_mock = MagicMock(return_value=5)
    monkeypatch.setattr("src.legal_fetcher.ingest_file_to_vector_db", ingest_mock)

    file_path = temp_legal_mgr.check_and_sync_corpus("ptk")

    manifest_path = temp_legal_mgr.legal_dir / ".legal_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "ptk" in manifest
    assert manifest["ptk"]["local_file"] == "ptk_2013_v.txt"
    ingest_mock.assert_called_once_with(file_path, temp_legal_mgr._settings, profile_id="legal")


def test_check_and_sync_corpus_cache_hit_no_redownload(
    temp_legal_mgr: LegalCorpusManager, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify cache hit does not re-download or re-ingest if remote is unchanged."""
    mock_bytes = _create_mock_legal_bytes()
    monkeypatch.setattr(
        temp_legal_mgr, "_fetch_content", lambda url, cid: (mock_bytes, "etag1", None)
    )
    ingest_mock = MagicMock(return_value=5)
    monkeypatch.setattr("src.legal_fetcher.ingest_file_to_vector_db", ingest_mock)

    file_path = temp_legal_mgr.check_and_sync_corpus("btk")
    assert ingest_mock.call_count == 1

    # Second sync: probe returns is_same=True
    monkeypatch.setattr(
        temp_legal_mgr, "_probe_remote_headers", lambda url, etag, last_mod: (True, etag, last_mod)
    )
    file_path2 = temp_legal_mgr.check_and_sync_corpus("btk")

    assert file_path2 == file_path
    assert ingest_mock.call_count == 1


def test_probe_remote_headers_304(temp_legal_mgr: LegalCorpusManager) -> None:
    """Verify HTTP 304 response returns is_same=True."""
    http_error = urllib.error.HTTPError("http://example.com", 304, "Not Modified", {}, None)
    with patch("urllib.request.urlopen", side_effect=http_error):
        is_same, etag, last_mod = temp_legal_mgr._probe_remote_headers(
            "http://example.com", etag="etag123", last_mod="Wed, 01 Jan 2026"
        )
        assert is_same is True
        assert etag == "etag123"
        assert last_mod == "Wed, 01 Jan 2026"


def test_sync_selected_corpora_batch(
    temp_legal_mgr: LegalCorpusManager, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify batch syncing multiple corpora."""
    mock_bytes = _create_mock_legal_bytes()
    monkeypatch.setattr(
        temp_legal_mgr, "_fetch_content", lambda url, cid: (mock_bytes, "etag1", None)
    )
    ingest_mock = MagicMock(return_value=3)
    monkeypatch.setattr("src.legal_fetcher.ingest_file_to_vector_db", ingest_mock)

    res = temp_legal_mgr.sync_selected_corpora(["ptk", "btk", "invalid_id"])
    assert res["status"] == "partial"
    assert "ptk" in res["synced"]
    assert "btk" in res["synced"]
    assert len(res["errors"]) == 1
    assert "invalid_id" in res["errors"][0]
    assert res["total_synced"] == 2
