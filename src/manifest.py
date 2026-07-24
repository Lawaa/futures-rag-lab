"""Change detection for the ingestion pipeline.

A lightweight MD5 fingerprint over the data directory (file names, sizes and
modification times) lets the app skip re-indexing when nothing has changed.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os

from .settings import Settings


def compute_fingerprint(settings: Settings) -> str:
    """Return an MD5 fingerprint of the data directory's current state."""
    if not settings.data_path.exists():
        return ""

    entries = []
    for filepath in sorted(glob.glob(os.path.join(settings.data_path, "*"))):
        if os.path.isfile(filepath):
            stat = os.stat(filepath)
            entries.append(f"{os.path.basename(filepath)}:{stat.st_size}:{stat.st_mtime}")

    combined = "|".join(entries)
    return hashlib.md5(combined.encode("utf-8")).hexdigest()


def is_data_changed(settings: Settings) -> bool:
    """Return ``True`` when the data directory differs from the saved manifest."""
    manifest = settings.manifest_path
    if not manifest.exists():
        return True

    try:
        stored = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return True

    return stored.get("fingerprint") != compute_fingerprint(settings)


def save_manifest(settings: Settings) -> None:
    """Persist the current data fingerprint alongside the vector store."""
    settings.manifest_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"fingerprint": compute_fingerprint(settings)}
    settings.manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")