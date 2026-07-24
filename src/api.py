"""FastAPI interface exposing the RAG assistant over HTTP."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from .bootstrap import build_service, ensure_vector_db
from .credentials import AuthenticationError, get_stored_api_key
from .llm import is_authentication_error
from .rag_service import DEFAULT_SESSION_ID, RagService
from .settings import get_settings


STATIC_DIR = Path(__file__).parent / "static"


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Prepare the database and build the RAG service on startup."""
    settings = get_settings()

    if not ensure_vector_db(settings):
        raise RuntimeError("No documents to ingest. Add files to the data directory.")

    api_key = None
    if settings.uses_gemini:
        api_key = get_stored_api_key()
        if not api_key:
            raise AuthenticationError(
                "No Gemini API key found. Set GEMINI_API_KEY, run the CLI once to "
                "store it, or switch to a local model with RAG_LLM_PROVIDER=ollama."
            )

    app.state.service = build_service(settings, api_key)
    yield


app = FastAPI(
    title="Futures Trading RAG API",
    description="Retrieval-Augmented Generation assistant for futures trading.",
    version="1.0.0",
    lifespan=lifespan,
)


def get_service(request: Request) -> RagService:
    """Resolve the shared :class:`RagService` from application state."""
    return request.app.state.service


ServiceDep = Annotated[RagService, Depends(get_service)]


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    """Serve the browser chat interface."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    """Lightweight liveness probe."""
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
    )


@app.post("/chat/stream")
async def chat_stream(payload: ChatRequest, service: ServiceDep) -> StreamingResponse:
    """Stream an answer token-by-token as plain text."""
    retrieval = service.retrieve(payload.question, payload.session_id)

    def token_generator():
        yield from service.stream_answer(payload.question, retrieval, payload.session_id)

    return StreamingResponse(token_generator(), media_type="text/plain")


@app.delete("/sessions/{session_id}")
async def reset_session(session_id: str, service: ServiceDep) -> dict[str, str]:
    """Clear the conversation history for a session."""
    service.reset_history(session_id)
    return {"status": "cleared", "session_id": session_id}