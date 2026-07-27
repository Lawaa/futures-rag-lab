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
from dataclasses import dataclass

from .logging_config import get_logger
from .settings import Settings

logger = get_logger(__name__)

DEFAULT_PROFILE_ID = "default"


@dataclass(frozen=True)
class Profile:
    """A named business/tenant profile.

    ``system_prompt`` overrides the default assistant persona used during answer
    generation; ``description`` is shown to the router so it can pick the right
    profile for an incoming question.
    """

    id: str
    name: str
    description: str = ""
    system_prompt: str | None = None


@dataclass(frozen=True)
class ProfileRegistry:
    """An immutable collection of profiles with an active selection."""

    profiles: tuple[Profile, ...]
    active_id: str

    @property
    def active(self) -> Profile:
        """The profile selected for this deployment (fallback: first profile)."""
        return self.get(self.active_id)

    def get(self, profile_id: str | None) -> Profile:
        """Return the profile with ``profile_id`` or the first profile as fallback."""
        for profile in self.profiles:
            if profile.id == profile_id:
                return profile
        return self.profiles[0]

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


def _builtin_default() -> Profile:
    """The single profile used when no profiles file is configured."""
    return Profile(
        id=DEFAULT_PROFILE_ID,
        name="Knowledge Base Assistant",
        description="General knowledge base built from the loaded documents.",
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
                description=str(entry.get("description", "")),
                system_prompt=entry.get("system_prompt"),
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
