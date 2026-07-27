"""FastAPI interface exposing the RAG assistant over HTTP."""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .bootstrap import build_service, ensure_vector_db
from .credentials import (
    AuthenticationError,
    get_stored_api_key,
    store_api_key,
)
from .llm import is_authentication_error, validate_api_key
from .rag_service import DEFAULT_SESSION_ID, RagService
from .settings import get_settings


STATIC_DIR = Path(__file__).parent / "static"
ASSETS_DIR = STATIC_DIR / "assets"

class NoCacheStaticFiles(StaticFiles):
    """Static files that must be revalidated so the UI never renders stale.

    Sends ``Cache-Control: no-cache`` so browsers always revalidate against the
    server's ETag before reusing a cached asset. This keeps 304 efficiency while
    preventing an old ``app.js``/``app.css`` from lingering after an update.
    """

    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-cache"
        return response

class ChatRequest(BaseModel):
    """Incoming chat request."""

    question: str = Field(..., min_length=1)
    session_id: str = Field(default=DEFAULT_SESSION_ID, min_length=1)


class SourceModel(BaseModel):
    """A referenced source document."""

    name: str
    page: int | None = None


class ChatResponse(BaseModel):
    """Assistant answer with supporting sources."""

    answer: str
    sources: list[SourceModel]
    # False when the answer relied on knowledge outside the loaded documents.
    grounded: bool = True


class ConversationSummary(BaseModel):
    """A saved conversation shown in the history list."""

    id: str
    title: str
    updated_at: str
    pinned: bool = False


class MessageModel(BaseModel):
    """A single stored chat message."""

    role: str
    content: str


class RenameRequest(BaseModel):
    """Request body for renaming a conversation."""

    title: str = Field(..., min_length=1, max_length=200)


class PinRequest(BaseModel):
    """Request body for pinning/unpinning a conversation."""

    pinned: bool


class ApiKeyRequest(BaseModel):
    """Request body for storing a Gemini API key at runtime."""

    api_key: str = Field(..., min_length=1)


def _build_service_state(app: FastAPI) -> None:
    """Assemble the RAG service into ``app.state``, recording setup blockers.

    The server always finishes starting so the UI can load; when a prerequisite
    is missing (no documents, or a Gemini key is required but absent) it records
    a machine-readable reason in ``app.state.setup_reason`` instead of crashing.
    This is what lets a freshly installed desktop build open its window and guide
    the user through first-run setup.
    """
    settings = get_settings()
    app.state.service = None
    app.state.setup_reason = None

    if not ensure_vector_db(settings):
        app.state.setup_reason = "no_documents"
        return

    api_key = get_stored_api_key() if settings.uses_gemini else None
    if settings.uses_gemini and not api_key:
        app.state.setup_reason = "needs_api_key"
        return

    try:
        app.state.service = build_service(settings, api_key)
    except AuthenticationError:
        app.state.setup_reason = "needs_api_key"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Prepare the database and build the RAG service on startup."""
    _build_service_state(app)
    yield


app = FastAPI(
    title="Futures Trading RAG API",
    description="Retrieval-Augmented Generation assistant for futures trading.",
    version="1.0.0",
    lifespan=lifespan,
)

# Safe defaults so readiness checks work before the lifespan runs (e.g. tests).
app.state.service = None
app.state.setup_reason = None

# Serve the app icon and other static assets used by the web UI.
app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> FileResponse:
    """Serve the knowledge-base icon as the browser favicon."""
    return FileResponse(ASSETS_DIR / "icon.png")


def get_service(request: Request) -> RagService:
    """Resolve the shared :class:`RagService` from application state."""
    service = getattr(request.app.state, "service", None)
    if service is None:
        raise HTTPException(
            status_code=503,
            detail="Assistant is not ready yet. Complete first-run setup.",
        )
    return service


ServiceDep = Annotated[RagService, Depends(get_service)]


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    """Serve the browser chat interface."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    """Lightweight liveness probe."""
    return {"status": "ok"}


@app.get("/config")
async def config(request: Request) -> dict[str, object]:
    """Expose runtime settings and readiness the web UI needs on load."""
    settings = get_settings()
    reason = getattr(request.app.state, "setup_reason", None)
    return {
        "language": settings.language,
        "provider": settings.llm_provider,
        "ready": getattr(request.app.state, "service", None) is not None,
        "needs_api_key": reason == "needs_api_key",
        "setup_reason": reason,
    }


@app.post(
    "/config/api-key",
    responses={
        400: {"description": "A key is not applicable for the active provider."},
        401: {"description": "The supplied API key was rejected by the provider."},
        503: {"description": "No documents are available to ingest."},
    },
)
async def set_api_key(payload: ApiKeyRequest, request: Request) -> dict[str, str]:
    """Store a Gemini API key and build the assistant so it becomes ready."""
    settings = get_settings()
    if not settings.uses_gemini:
        raise HTTPException(
            status_code=400,
            detail="An API key is only required for the Gemini provider.",
        )
    if not validate_api_key(payload.api_key, settings):
        raise HTTPException(status_code=401, detail="The API key was rejected.")

    store_api_key(payload.api_key)
    if not ensure_vector_db(settings):
        raise HTTPException(
            status_code=503,
            detail="No documents to ingest. Add files to the data directory.",
        )
    request.app.state.service = build_service(settings, payload.api_key)
    request.app.state.setup_reason = None
    return {"status": "ok"}


@app.post(
    "/chat",
    responses={
        401: {"description": "Invalid or missing API key."},
        500: {"description": "Unexpected error while generating an answer."},
    },
)
async def chat(payload: ChatRequest, service: ServiceDep) -> ChatResponse:
    """Answer a question and return supporting sources."""
    try:
        answer = service.answer(payload.question, payload.session_id)
    except Exception as error:
        if is_authentication_error(error):
            raise HTTPException(status_code=401, detail="Invalid or missing API key.") from error
        raise HTTPException(status_code=500, detail=str(error)) from error

    return ChatResponse(
        answer=answer.text,
        sources=[SourceModel(name=s.name, page=s.page) for s in answer.sources],
        grounded=answer.grounded,
    )


@app.post("/chat/stream")
async def chat_stream(payload: ChatRequest, service: ServiceDep) -> StreamingResponse:
    """Stream an answer token-by-token as plain text."""
    retrieval = service.retrieve(payload.question, payload.session_id)

    def token_generator():
        yield from service.stream_answer(payload.question, retrieval, payload.session_id)

    return StreamingResponse(token_generator(), media_type="text/plain")


@app.post("/chat/events")
async def chat_events(payload: ChatRequest, service: ServiceDep) -> StreamingResponse:
    """Stream the whole turn as newline-delimited JSON progress events.

    Each line is one event: ``status`` (pipeline stage), ``token`` (answer
    chunk), ``done`` (sources + groundedness) or ``error``. This lets the web UI
    show live retrieval progress before the answer streams in.
    """

    def event_generator():
        try:
            for event in service.stream_events(payload.question, payload.session_id):
                yield json.dumps(event) + "\n"
        except Exception as error:  # surface failures inside the stream
            if is_authentication_error(error):
                event = {"type": "error", "code": "auth", "detail": "Invalid or missing API key."}
            else:
                event = {"type": "error", "detail": str(error)}
            yield json.dumps(event) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")


@app.delete("/sessions/{session_id}")
async def reset_session(session_id: str, service: ServiceDep) -> dict[str, str]:
    """Clear the conversation history for a session."""
    service.reset_history(session_id)
    return {"status": "cleared", "session_id": session_id}


@app.get("/conversations")
async def list_conversations(service: ServiceDep) -> list[ConversationSummary]:
    """Return the most recent saved conversations (newest first)."""
    return [ConversationSummary(**item) for item in service.list_conversations()]


@app.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str, service: ServiceDep
) -> list[MessageModel]:
    """Return the stored messages for a conversation so it can be resumed."""
    return [
        MessageModel(role=role, content=content)
        for role, content in service.get_messages(conversation_id)
    ]


@app.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str, service: ServiceDep
) -> dict[str, str]:
    """Permanently delete a saved conversation."""
    service.delete_conversation(conversation_id)
    return {"status": "deleted", "conversation_id": conversation_id}


@app.patch("/conversations/{conversation_id}")
async def rename_conversation(
    conversation_id: str, payload: RenameRequest, service: ServiceDep
) -> dict[str, str]:
    """Rename a saved conversation."""
    title = service.rename_conversation(conversation_id, payload.title)
    if title is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"status": "renamed", "conversation_id": conversation_id, "title": title}


@app.patch("/conversations/{conversation_id}/pin")
async def pin_conversation(
    conversation_id: str, payload: PinRequest, service: ServiceDep
) -> dict[str, object]:
    """Pin or unpin a conversation so it is exempt from automatic pruning."""
    if not service.set_pinned(conversation_id, payload.pinned):
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {
        "status": "pinned" if payload.pinned else "unpinned",
        "conversation_id": conversation_id,
        "pinned": payload.pinned,
    }