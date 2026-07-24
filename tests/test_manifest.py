"""Tests for ingestion change detection (manifest)."""

from __future__ import annotations

from src.manifest import compute_fingerprint, is_data_changed, save_manifest
from src.settings import Settings


def test_fingerprint_empty_when_no_data(settings: Settings) -> None:
    assert compute_fingerprint(settings) == ""


def test_is_data_changed_true_without_manifest(settings: Settings) -> None:
    assert is_data_changed(settings) is True


def test_manifest_roundtrip_detects_no_change(settings: Settings) -> None:
    settings.data_path.mkdir(parents=True)
    (settings.data_path / "doc.txt").write_text("hello", encoding="utf-8")

    save_manifest(settings)
    assert is_data_changed(settings) is False


def test_manifest_detects_new_file(settings: Settings) -> None:
    settings.data_path.mkdir(parents=True)
    (settings.data_path / "doc.txt").write_text("hello", encoding="utf-8")
    save_manifest(settings)

    (settings.data_path / "extra.txt").write_text("more", encoding="utf-8")
    assert is_data_changed(settings) is True