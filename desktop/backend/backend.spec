# PyInstaller spec for the bundled RAG backend sidecar.
#
# Build from the repository root:
#     uv run pyinstaller desktop/backend/backend.spec --noconfirm --clean
#
# Keep the freeze lean: embeddings use FastEmbed/ONNX (not PyTorch). Filter out
# Google API discovery JSON and other unused trees that ``collect_all`` would
# otherwise ship. The vector DB and embedding weights are created/downloaded in
# the per-user data directory at runtime — not baked into this binary.
#
# PyInstaller resolves relative paths against SPECPATH (this file's directory),
# not the process cwd. Anchor everything at the repo root.

import os
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules

REPO_ROOT = Path(SPECPATH).resolve().parents[1]

datas = [
    (str(REPO_ROOT / "src" / "static"), "src/static"),  # web UI assets
    (str(REPO_ROOT / "data"), "data"),                  # default starter documents
]
binaries = []
hiddenimports = ["src", "src.api", "fastembed", "onnxruntime"]

_BUNDLE_PACKAGES = (
    "chromadb",
    "fastembed",
    "onnxruntime",
    "langchain",
    "langchain_core",
    "langchain_chroma",
    "langchain_google_genai",
    "langchain_ollama",
    "langchain_text_splitters",
    "langgraph",
    "huggingface_hub",
    "tokenizers",
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
# ``langgraph-checkpoint-sqlite`` distribution.
for package in ("langgraph.checkpoint.sqlite", "langgraph.checkpoint.serde"):
    hiddenimports += collect_submodules(package)
hiddenimports += ["langgraph.checkpoint.base", "langgraph.checkpoint.sqlite"]


def _is_bloat(src: str) -> bool:
    """Drop trees that are unused at runtime but inflate the one-file sidecar."""
    path = os.path.normpath(src).replace("\\", "/").lower()
    if path.endswith(".lib"):
        return True
    deny_substrings = (
        "googleapiclient/discovery_cache",
        "/torch/",
        "site-packages/torch/",
        "torchvision/",
        "torchaudio/",
        "site-packages/transformers/",
        "sentence_transformers/",
        "site-packages/sklearn/",
        "site-packages/scipy/",
        "matplotlib/",
        "tensorboard",
        "site-packages/nvidia/",
        "/triton/",
        "torch/include",
        "torch/testing",
        "torch/_inductor",
        "torch/distributed",
        "torch/_dynamo",
    )
    return any(s in path for s in deny_substrings)


datas = [(src, dest) for src, dest in datas if not _is_bloat(src)]
binaries = [(src, dest) for src, dest in binaries if not _is_bloat(src)]

# Heavy ML stacks must not be pulled in via stray imports during Analysis.
excludes = [
    "tkinter",
    "torch",
    "torchvision",
    "torchaudio",
    "transformers",
    "sentence_transformers",
    "sklearn",
    "scipy",
    "matplotlib",
    "IPython",
    "notebook",
    "pytest",
    "pandas",
    "triton",
    "nvidia",
    "tensorboard",
    "langchain_huggingface",
]


a = Analysis(
    [str(REPO_ROOT / "desktop" / "backend" / "entry.py")],
    pathex=[str(REPO_ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)

# Second pass: Analysis may still attach torch/google discovery via dependency
# hooks even when packages are excluded from collect_all.
a.datas = [(src, dest, typ) for src, dest, typ in a.datas if not _is_bloat(src)]
a.binaries = [(src, dest, typ) for src, dest, typ in a.binaries if not _is_bloat(src)]

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
