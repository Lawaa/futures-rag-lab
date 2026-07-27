"""Build the Python backend into a Tauri sidecar binary.

Run from anywhere:

    uv run python desktop/scripts/build_backend.py

Steps performed:

1. Freeze ``desktop/backend/entry.py`` and all dependencies into a single
   executable using PyInstaller (``desktop/backend/backend.spec``).
2. Copy the result into ``desktop/src-tauri/binaries`` renamed to the
   target-triple convention Tauri expects for sidecars
   (e.g. ``rag-backend-x86_64-pc-windows-msvc.exe``).

Tauri resolves the sidecar for the current platform at build time, so the same
command works unchanged on Windows, macOS and Linux CI runners.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC = REPO_ROOT / "desktop" / "backend" / "backend.spec"
SIDECAR_DIR = REPO_ROOT / "desktop" / "src-tauri" / "binaries"
BINARY_STEM = "rag-backend"


def _target_triple() -> str:
    """Return the Rust host target triple (matches Tauri's sidecar naming)."""
    output = subprocess.check_output(["rustc", "-Vv"], text=True)
    for line in output.splitlines():
        if line.startswith("host:"):
            return line.split(":", 1)[1].strip()
    raise RuntimeError("Could not determine the Rust target triple from `rustc -Vv`.")


def _run_pyinstaller() -> None:
    subprocess.run(
        [sys.executable, "-m", "PyInstaller", str(SPEC), "--noconfirm", "--clean"],
        cwd=REPO_ROOT,
        check=True,
    )


def main() -> None:
    _run_pyinstaller()

    suffix = ".exe" if os.name == "nt" else ""
    built = REPO_ROOT / "dist" / f"{BINARY_STEM}{suffix}"
    if not built.exists():
        raise FileNotFoundError(f"PyInstaller output not found: {built}")

    triple = _target_triple()
    SIDECAR_DIR.mkdir(parents=True, exist_ok=True)
    destination = SIDECAR_DIR / f"{BINARY_STEM}-{triple}{suffix}"
    shutil.copy2(built, destination)
    destination.chmod(0o755)

    print(f"Sidecar ready: {destination}")


if __name__ == "__main__":
    main()
