# PyInstaller spec for the bundled RAG backend sidecar.
#
# Build from the repository root:
#     uv run pyinstaller desktop/backend/backend.spec --noconfirm --clean
#
# The heavy ML/LLM dependencies (chromadb, sentence-transformers, langchain, ...)
# ship data files and dynamic imports that PyInstaller cannot discover on its
# own, so we use ``collect_all`` to pull each package in wholesale. The result is
# a single ``dist/rag-backend`` executable containing Python and every
# dependency — the artifact the Tauri shell launches as a sidecar.

from PyInstaller.utils.hooks import collect_all, collect_submodules

datas = [
    ("src/static", "src/static"),  # web UI assets
    ("data", "data"),              # default starter documents (seeded on first run)
]
binaries = []
hiddenimports = ["src", "src.api"]

_BUNDLE_PACKAGES = (
    "chromadb",
    "langchain",
    "langchain_core",
    "langchain_chroma",
    "langchain_google_genai",
    "langchain_huggingface",
    "langchain_ollama",
    "langchain_text_splitters",
    "langgraph",
    "sentence_transformers",
    "transformers",
    "tokenizers",
    "huggingface_hub",
    "keyring",
    "pydantic",
    "pydantic_settings",
    "pypdf",
    "fastapi",
    "uvicorn",
)

for package in _BUNDLE_PACKAGES:
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(package)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

hiddenimports += collect_submodules("uvicorn")

# ``langgraph`` and ``langgraph.checkpoint`` are PEP-420 namespace packages
# (no ``__init__.py``), so ``collect_all("langgraph")`` above does not reliably
# discover the SQLite checkpointer, which ships as the separate
# ``langgraph-checkpoint-sqlite`` distribution. The conversation checkpointer
# (enabled by default) imports ``langgraph.checkpoint.sqlite`` at startup, so we
# collect these subpackages explicitly to guarantee they land in the bundle.
for package in ("langgraph.checkpoint.sqlite", "langgraph.checkpoint.serde"):
    hiddenimports += collect_submodules(package)
hiddenimports += ["langgraph.checkpoint.base", "langgraph.checkpoint.sqlite"]


a = Analysis(
    ["desktop/backend/entry.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="rag-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,  # keep a console so backend logs are visible if launched directly
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
