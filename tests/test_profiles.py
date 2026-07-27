"""Tests for tenant/business profile loading and routing selection."""

from __future__ import annotations

import json
from pathlib import Path

from src.profiles import DEFAULT_PROFILE_ID, load_profiles
from src.settings import Settings


def test_missing_profiles_file_yields_single_default(tmp_path: Path) -> None:
    settings = Settings(profiles_path=tmp_path / "none.json")
    registry = load_profiles(settings)

    assert registry.routable is False
    assert registry.active.id == DEFAULT_PROFILE_ID


def test_profiles_loaded_from_json(tmp_path: Path) -> None:
    path = tmp_path / "profiles.json"
    path.write_text(
        json.dumps(
            [
                {"id": "trading", "name": "Trading", "description": "Futures desk",
                 "system_prompt": "You are a futures expert."},
                {"id": "legal", "name": "Legal", "description": "Contracts"},
            ]
        ),
        encoding="utf-8",
    )
    settings = Settings(profiles_path=path, profile="legal")
    registry = load_profiles(settings)

    assert registry.routable is True
    assert registry.active.id == "legal"
    assert registry.get("trading").system_prompt == "You are a futures expert."
    # Unknown ids fall back to the first profile.
    assert registry.get("unknown").id == "trading"


def test_invalid_profiles_file_falls_back_to_default(tmp_path: Path) -> None:
    path = tmp_path / "profiles.json"
    path.write_text("{ not valid json", encoding="utf-8")
    settings = Settings(profiles_path=path)

    registry = load_profiles(settings)

    assert registry.routable is False
    assert registry.active.id == DEFAULT_PROFILE_ID


def test_unknown_active_profile_falls_back_to_first(tmp_path: Path) -> None:
    path = tmp_path / "profiles.json"
    path.write_text(json.dumps([{"id": "a"}, {"id": "b"}]), encoding="utf-8")
    settings = Settings(profiles_path=path, profile="does-not-exist")

    registry = load_profiles(settings)

    assert registry.active.id == "a"
