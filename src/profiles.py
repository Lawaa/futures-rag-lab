"""Tenant/business profiles: per-deployment identity and system prompt.

A single build of this assistant can be shipped to different businesses. Each
business is described by a :class:`Profile` that customises the assistant's
persona (system prompt) and display name without touching code. Profiles are
loaded from an optional JSON file (``settings.profiles_path``); when it is
absent a single built-in ``default`` profile is used, preserving the original
behaviour.

When ``enable_profile_routing`` is on and more than one profile is defined, the
retrieval graph classifies each question and routes it to the best-matching
profile, so one deployment can serve several business domains at once.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from .logging_config import get_logger
from .settings import Settings

logger = get_logger(__name__)

DEFAULT_PROFILE_ID = "default"


class Profile(BaseModel):
    """A named business/tenant profile with domain persona and guardrails.

    ``system_prompt`` overrides the default assistant persona during answer
    generation; ``description`` is shown to the router; ``guardrails`` configure
    domain-specific rules (e.g. enforce_citations, anonymize_phi).
    """

    id: str
    name: str
    names: dict[str, str] = Field(default_factory=dict)
    description: str = ""
    descriptions: dict[str, str] = Field(default_factory=dict)
    system_prompt: str | None = None
    system_prompts: dict[str, str] = Field(default_factory=dict)
    guardrails: dict[str, Any] = Field(default_factory=dict)

    def get_name(self, language: str = "en") -> str:
        """Return language-specific name or fall back to default name."""
        if self.names and language in self.names:
            return self.names[language]
        return self.name

    def get_description(self, language: str = "en") -> str:
        """Return language-specific description or fall back to default description."""
        if self.descriptions and language in self.descriptions:
            return self.descriptions[language]
        return self.description

    def get_system_prompt(self, language: str = "en") -> str | None:
        """Return language-specific system prompt or fall back to default system_prompt."""
        if self.system_prompts and language in self.system_prompts:
            return self.system_prompts[language]
        return self.system_prompt


class ProfileRegistry:
    """A collection of tenant/domain profiles with an active selection."""

    def __init__(self, profiles: tuple[Profile, ...] | list[Profile], active_id: str) -> None:
        self.profiles: tuple[Profile, ...] = tuple(profiles)
        self.active_id: str = active_id

    @property
    def active(self) -> Profile:
        """The profile selected for this deployment (fallback: first profile)."""
        return self.get(self.active_id)

    def get(self, profile_id: str | None) -> Profile:
        """Return the profile with ``profile_id`` or the first profile as fallback."""
        for profile in self.profiles:
            if profile.id == profile_id:
                return profile
        return self.profiles[0] if self.profiles else _builtin_default()

    @property
    def routable(self) -> bool:
        """Whether there is more than one profile to choose between."""
        return len(self.profiles) > 1

    def listing(self) -> str:
        """A newline-separated ``id: description`` catalogue for the router."""
        return "\n".join(
            f"- {profile.id}: {profile.description or profile.name}"
            for profile in self.profiles
        )

    def list_profiles(self) -> list[Profile]:
        """Return all registered profiles as a list."""
        return list(self.profiles)

    def add_or_update(self, new_profile: Profile) -> ProfileRegistry:
        """Return a new ProfileRegistry with the given profile added or updated."""
        updated: list[Profile] = []
        found = False
        for p in self.profiles:
            if p.id == new_profile.id:
                updated.append(new_profile)
                found = True
            else:
                updated.append(p)
        if not found:
            updated.append(new_profile)

        active = self.active_id if any(p.id == self.active_id for p in updated) else updated[0].id
        return ProfileRegistry(profiles=tuple(updated), active_id=active)

    def save_to_disk(self, path: Path) -> None:
        """Persist registered profiles to a JSON file."""
        data = [p.model_dump() for p in self.profiles]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _builtin_default() -> Profile:
    """The single profile used when no profiles file is configured."""
    return Profile(
        id=DEFAULT_PROFILE_ID,
        name="General Futures Assistant",
        names={
            "en": "General Futures Assistant",
            "hu": "Általános Kereskedési Asszisztens",
        },
        description="General knowledge base built from the loaded documents.",
        descriptions={
            "en": "General knowledge base built from the loaded documents.",
            "hu": "Általános tudásbázis a betöltött dokumentumok alapján.",
        },
        system_prompt="You are an expert Futures Trading Assistant.",
        system_prompts={},
        guardrails={"enforce_citations": False, "anonymize_phi": False},
    )


def _parse_profiles(raw: object) -> list[Profile]:
    """Convert decoded JSON into a list of :class:`Profile` objects."""
    if not isinstance(raw, list):
        raise ValueError("Profiles file must contain a JSON array.")
    profiles: list[Profile] = []
    for entry in raw:
        if not isinstance(entry, dict) or "id" not in entry:
            raise ValueError("Each profile needs at least an 'id' field.")
        profile_id = str(entry["id"])
        profiles.append(
            Profile(
                id=profile_id,
                name=str(entry.get("name", profile_id)),
                names=entry.get("names") or {},
                description=str(entry.get("description", "")),
                descriptions=entry.get("descriptions") or {},
                system_prompt=entry.get("system_prompt"),
                system_prompts=entry.get("system_prompts") or {},
                guardrails=entry.get("guardrails") or {},
            )
        )
    return profiles


def load_profiles(settings: Settings) -> ProfileRegistry:
    """Build the profile registry from ``settings.profiles_path`` (or defaults)."""
    profiles: list[Profile] = []
    path = settings.profiles_path
    if path and path.exists():
        try:
            profiles = _parse_profiles(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, ValueError) as error:
            logger.warning("Ignoring invalid profiles file %s: %s", path, error)
            profiles = []

    if not profiles:
        profiles = [_builtin_default()]

    known_ids = {profile.id for profile in profiles}
    active = settings.profile if settings.profile in known_ids else profiles[0].id
    return ProfileRegistry(profiles=tuple(profiles), active_id=active)
