"""PyInstaller entry point for the bundled desktop backend.

This module is what the Tauri desktop shell launches as a *sidecar*. It exists so
the packaged application can:

* **Run in any environment.** The Python interpreter and every dependency are
  frozen into a single executable by PyInstaller, so end users never install
  Python, ``uv``, or any package. This is what "solves the different
  environments problem": the machine only runs a self-contained binary.

* **Keep a user-writable data directory.** The application *code* is bundled and
  effectively hidden inside the executable, but the source **documents** live in
  a normal folder under the user's account. Technical users can still add or
  remove files there to expand the knowledge base, exactly like editing the
  ``data/`` folder in a source checkout. On the next launch the backend detects
  the change and re-indexes automatically.

The executable is intentionally thin: it resolves the per-user data/database
locations, seeds the default documents on first launch, points the existing
settings layer at those locations via ``RAG_*`` environment variables, and then
starts the very same FastAPI application used by the source install.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

APP_DIR_NAME = "FuturesTradingAssistant"


def user_data_root() -> Path:
    """Return the per-user, writable application directory for this platform.

    The location follows each operating system's convention so the folder is
    easy for technical users to find and back up:

    * Windows: ``%APPDATA%\\FuturesTradingAssistant``
    * macOS:   ``~/Library/Application Support/FuturesTradingAssistant``
    * Linux:   ``$XDG_DATA_HOME/FuturesTradingAssistant`` (or ``~/.local/share``)
    """
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    elif sys.platform == "darwin":
        base = str(Path.home() / "Library" / "Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return Path(base) / APP_DIR_NAME


def _bundled_root() -> Path:
    """Return the directory that holds bundled resources (default documents)."""
    if getattr(sys, "frozen", False):
        # PyInstaller extracts bundled data files under ``sys._MEIPASS``.
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parents[2]


def _seed_default_documents(data_dir: Path) -> None:
    """Copy the shipped starter documents into an empty user data directory.

    Existing folders are left untouched so a user's own documents are never
    overwritten on upgrade.
    """
    if data_dir.exists() and any(data_dir.iterdir()):
        return
    data_dir.mkdir(parents=True, exist_ok=True)
    seed = _bundled_root() / "data"
    if not seed.exists():
        return
    for item in seed.iterdir():
        if item.is_file():
            shutil.copy2(item, data_dir / item.name)


def configure_environment() -> tuple[str, int]:
    """Point the settings layer at user-writable locations and return host/port."""
    root = user_data_root()
    data_dir = root / "data"
    db_dir = root / "chroma_db"

    _seed_default_documents(data_dir)
    db_dir.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("RAG_DATA_PATH", str(data_dir))
    os.environ.setdefault("RAG_DB_PATH", str(db_dir))

    host = os.environ.setdefault("RAG_API_HOST", "127.0.0.1")
    port = int(os.environ.setdefault("RAG_API_PORT", "8000"))
    return host, port


def main() -> None:
    """Configure the environment and start the API server (blocking)."""
    host, port = configure_environment()

    # Import after the environment is configured so cached settings pick up the
    # user-writable paths.
    import uvicorn

    from src.api import app

    uvicorn.run(app, host=host, port=port, reload=False, log_level="info")


if __name__ == "__main__":
    main()
