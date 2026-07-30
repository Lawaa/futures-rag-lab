# Desktop packaging (Tauri)

This folder turns the Futures Trading Assistant into **native, cross-platform
installers** (Windows, macOS, Linux). The application code and its Python runtime
are frozen into a self-contained sidecar binary, wrapped in a small
[Tauri](https://tauri.app/) desktop shell, so end users install one file and need
nothing else preinstalled.

## Layout

| Path | Purpose |
| --- | --- |
| `backend/entry.py` | Sidecar entry point: resolves the user data dir, seeds default docs, starts the API server |
| `backend/backend.spec` | PyInstaller spec that freezes the backend + all dependencies |
| `scripts/build_backend.py` | Builds the sidecar and copies it into `src-tauri/binaries` with the target-triple name |
| `src-tauri/` | Tauri shell: config, Rust source, capabilities, icons |
| `frontend/index.html` | Splash screen shown while the backend starts |
| `app-icon.png` | Source image used to generate the platform icon set |

## Build locally

Prerequisites: [Rust](https://www.rust-lang.org/tools/install) (`cargo` on
`PATH`), [Node.js](https://nodejs.org/), and the
[Tauri system dependencies](https://tauri.app/start/prerequisites/) for your
platform. On Windows that includes the MSVC C++ build tools. Restart the
terminal after installing Rust so `%USERPROFILE%\.cargo\bin` is on `PATH`.

```bash
# from the repository root
uv sync --dev

# from this folder (activate the project venv first so `python` finds PyInstaller)
npm install
npm run tauri icon app-icon.png   # once, to generate icons
npm run tauri build               # freezes the backend, then builds the installer
```

Installers are written to `src-tauri/target/release/bundle/`.

## Release

Push a version tag to build and publish installers for all platforms via
`.github/workflows/release.yml`:

```bash
git tag v0.1.0 && git push origin v0.1.0
```

See [../docs/DESKTOP.md](../docs/DESKTOP.md) for the complete guide, including the
user data directory, the first-run setup flow, and code-signing notes.
