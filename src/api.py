"""FastAPI interface exposing the RAG assistant over HTTP."""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from botocore.exceptions import NoCredentialsError

from .benchmarks.evaluator import BenchmarkSuiteResult
from .benchmarks.reporter import BenchmarkReporter
from .bootstrap import build_service, ensure_vector_db
from .cli import _persist_aws_credentials_to_file
from .credentials import (
    AuthenticationError,
    get_stored_api_key,
    store_api_key,
)
from .ingest import ingest_bytes_to_vector_db, ingest_file_to_vector_db
from .llm import is_authentication_error, validate_api_key
from .logging_config import get_logger
from .profiles import Profile
from .rag_service import DEFAULT_SESSION_ID, RagService
from .s3_service import S3StorageService
from .settings import Settings, get_settings

logger = get_logger(__name__)


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
    profile_id: str | None = Field(default=None, description="Optional tenant/domain profile ID.")


class SourceModel(BaseModel):
    """A referenced source document."""

    name: str
    page: int | None = None
    snippet: str | None = None



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


class SetupConfigRequest(BaseModel):
    """Payload for full runtime setup and onboarding configuration."""

    language: str = Field(default="en")
    llm_provider: str = Field(default="gemini")
    model: str | None = None
    api_key: str | None = None
    use_s3_storage: bool = Field(default=False)
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region: str | None = None
    aws_s3_bucket_name: str | None = None
    app_name: str | None = None


class OnboardingConfigRequest(SetupConfigRequest):
    """Payload to configure assistant during browser onboarding (backwards compatible)."""


class AppNameRequest(BaseModel):
    """Payload to update application display name."""

    app_name: str = Field(..., min_length=1)


class ProfileModel(BaseModel):
    """Payload for creating or updating a tenant/domain profile."""

    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: str = Field(default="")
    system_prompt: str | None = None
    guardrails: dict[str, Any] = Field(default_factory=dict)


class ProfileListResponse(BaseModel):
    """Available tenant profiles and current active default."""

    active_id: str
    profiles: list[ProfileModel]


class DocumentInfo(BaseModel):
    """Metadata for a stored document."""

    filename: str
    size: int
    last_modified: str
    profile_id: str | None = None


class DocumentListResponse(BaseModel):
    """Response containing list of documents."""

    documents: list[DocumentInfo]
    storage_type: str = "local"


class UploadResponse(BaseModel):
    """Response after successful document upload."""

    filename: str
    storage: str = "local"
    storage_type: str = "local"
    status: str = "success"
    message: str
    profile_id: str | None = None


class BenchmarkReportResponse(BaseModel):
    """Rendered embedding benchmark report and evaluation data."""

    report_markdown: str
    has_results: bool
    available: bool = False
    overall_winner: dict[str, Any] | None = None
    top_3_models: list[dict[str, Any]] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict)



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
    app.state.s3_service = None

    # Initialize S3 service if enabled
    if settings.use_s3_storage:
        try:
            app.state.s3_service = S3StorageService(settings)
            if not app.state.s3_service.check_bucket_access():
                app.state.setup_reason = "s3_bucket_not_accessible"
                return
        except ValueError as e:
            app.state.setup_reason = "s3_credentials_missing"
            logger.error("S3 service initialization failed: %s", e)
            return
        except Exception as e:
            app.state.setup_reason = "s3_initialization_error"
            logger.error("Unexpected error initializing S3 service: %s", e)
            return

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


def get_s3_service(request: Request) -> S3StorageService | None:
    """Resolve the S3 service from application state if enabled."""
    return getattr(request.app.state, "s3_service", None)


S3ServiceDep = Annotated[S3StorageService | None, Depends(get_s3_service)]


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
    ready = getattr(request.app.state, "service", None) is not None
    setup_required = (not settings.setup_completed) or (not ready) or (reason is not None)
    return {
        "language": settings.language,
        "provider": settings.llm_provider,
        "model": settings.active_model,
        "app_name": settings.app_name,
        "use_s3_storage": settings.use_s3_storage,
        "ready": ready,
        "needs_api_key": reason == "needs_api_key",
        "setup_reason": reason,
        "setup_required": setup_required,
    }


def _format_setup_env_lines(settings: Settings) -> list[str]:
    """Generate configuration lines for .env file."""
    lines = [
        "RAG_SETUP_COMPLETED=true",
        f"RAG_LANGUAGE={settings.language}",
        f"RAG_LLM_PROVIDER={settings.llm_provider}",
        f"RAG_USE_S3_STORAGE={str(settings.use_s3_storage).lower()}",
    ]
    model_key = "RAG_GEMINI_MODEL" if settings.uses_gemini else "RAG_OLLAMA_MODEL"
    lines.append(f"{model_key}={settings.active_model}")
    if settings.app_name:
        lines.append(f"RAG_APP_NAME={settings.app_name}")
    if settings.use_s3_storage:
        lines.append(f"RAG_AWS_ACCESS_KEY_ID={settings.aws_access_key_id or ''}")
        lines.append(f"RAG_AWS_REGION={settings.aws_region or ''}")
        lines.append(f"RAG_AWS_S3_BUCKET_NAME={settings.aws_s3_bucket_name or ''}")
    return lines


def _persist_setup_to_env(settings: Settings, env_path: Path | None = None) -> None:
    """Write non-sensitive setup configuration to .env for persistence."""
    target_env = env_path or Path(".env")
    lines: list[str] = target_env.read_text(encoding="utf-8").splitlines() if target_env.exists() else []

    keys = {
        "RAG_SETUP_COMPLETED", "RAG_LANGUAGE", "RAG_LLM_PROVIDER",
        "RAG_GEMINI_MODEL", "RAG_OLLAMA_MODEL", "RAG_USE_S3_STORAGE",
        "RAG_AWS_ACCESS_KEY_ID", "RAG_AWS_SECRET_ACCESS_KEY",
        "RAG_AWS_REGION", "RAG_AWS_S3_BUCKET_NAME", "RAG_APP_NAME",
    }
    filtered = [ln for ln in lines if not any(ln.startswith(k + "=") for k in keys)]
    filtered.extend(_format_setup_env_lines(settings))
    target_env.write_text("\n".join(filtered) + "\n", encoding="utf-8")


def _apply_s3_env(payload: SetupConfigRequest) -> None:
    """Set S3 environment variables if provided."""
    import os

    mapping = {
        "RAG_AWS_ACCESS_KEY_ID": payload.aws_access_key_id,
        "RAG_AWS_SECRET_ACCESS_KEY": payload.aws_secret_access_key,
        "RAG_AWS_REGION": payload.aws_region,
        "RAG_AWS_S3_BUCKET_NAME": payload.aws_s3_bucket_name,
    }
    for k, v in mapping.items():
        if v:
            os.environ[k] = v.strip()


def _apply_setup_env(payload: SetupConfigRequest) -> None:
    """Apply setup configuration values to environment variables."""
    import os

    if payload.language in ("en", "hu"):
        os.environ["RAG_LANGUAGE"] = payload.language
    if payload.llm_provider in ("gemini", "ollama"):
        os.environ["RAG_LLM_PROVIDER"] = payload.llm_provider
    if payload.model:
        model_key = "RAG_GEMINI_MODEL" if payload.llm_provider == "gemini" else "RAG_OLLAMA_MODEL"
        os.environ[model_key] = payload.model.strip()
    os.environ["RAG_USE_S3_STORAGE"] = str(payload.use_s3_storage).lower()
    os.environ["RAG_SETUP_COMPLETED"] = "true"
    if payload.app_name:
        os.environ["RAG_APP_NAME"] = payload.app_name.strip()
    if payload.use_s3_storage:
        _apply_s3_env(payload)


def _apply_setup_credentials(payload: SetupConfigRequest, settings: Settings) -> None:
    """Store credentials in keyring and AWS credentials file."""
    if payload.api_key and settings.uses_gemini:
        if not validate_api_key(payload.api_key, settings):
            raise HTTPException(
                status_code=401,
                detail="The supplied API key was rejected by Google Gemini.",
            )
        store_api_key(payload.api_key)

    if payload.use_s3_storage and payload.aws_access_key_id and payload.aws_secret_access_key:
        _persist_aws_credentials_to_file(
            payload.aws_access_key_id.strip(), payload.aws_secret_access_key.strip()
        )


@app.post("/config/setup")
async def configure_setup(
    payload: SetupConfigRequest, request: Request
) -> dict[str, Any]:
    """Persist chosen onboarding settings to .env / keyring and initialize services."""
    _apply_setup_env(payload)
    get_settings.cache_clear()
    settings = get_settings()

    _apply_setup_credentials(payload, settings)
    _persist_setup_to_env(settings)
    _build_service_state(request.app)

    return {
        "status": "ok",
        "setup_required": False,
        "ready": getattr(request.app.state, "service", None) is not None,
        "setup_reason": getattr(request.app.state, "setup_reason", None),
        "language": settings.language,
        "provider": settings.llm_provider,
        "model": settings.active_model,
        "app_name": settings.app_name,
        "use_s3_storage": settings.use_s3_storage,
    }


@app.post("/config/onboarding")
async def apply_onboarding(
    payload: OnboardingConfigRequest, request: Request
) -> dict[str, Any]:
    """Handle first-run browser onboarding wizard setup (alias for /config/setup)."""
    return await configure_setup(payload, request)


@app.post("/config/app-name")
async def set_app_name(payload: AppNameRequest) -> dict[str, str]:
    """Update application display name dynamically."""
    import os

    os.environ["RAG_APP_NAME"] = payload.app_name.strip()
    get_settings.cache_clear()
    return {"status": "ok", "app_name": payload.app_name.strip()}


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
        try:
            answer = service.answer(
                payload.question, payload.session_id, profile_id=payload.profile_id
            )
        except TypeError:
            answer = service.answer(payload.question, payload.session_id)
    except Exception as error:
        if is_authentication_error(error):
            raise HTTPException(status_code=401, detail="Invalid or missing API key.") from error
        raise HTTPException(status_code=500, detail=str(error)) from error

    return ChatResponse(
        answer=answer.text,
        sources=[SourceModel(name=s.name, page=s.page, snippet=getattr(s, "snippet", None)) for s in answer.sources],
        grounded=answer.grounded,
    )


@app.post("/chat/stream")
async def chat_stream(payload: ChatRequest, service: ServiceDep) -> StreamingResponse:
    """Stream an answer token-by-token as plain text."""
    try:
        retrieval = service.retrieve(
            payload.question, payload.session_id, profile_id=payload.profile_id
        )
    except TypeError:
        retrieval = service.retrieve(payload.question, payload.session_id)

    def token_generator():
        try:
            yield from service.stream_answer(
                payload.question, retrieval, payload.session_id, profile_id=payload.profile_id
            )
        except TypeError:
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
            try:
                events = service.stream_events(
                    payload.question, payload.session_id, profile_id=payload.profile_id
                )
            except TypeError:
                events = service.stream_events(payload.question, payload.session_id)
            for event in events:
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


# --- Tenant & Profile Management Endpoints ---------------------------------


@app.get("/profiles")
async def list_profiles(service: ServiceDep) -> ProfileListResponse:
    """List all available tenant/domain profiles and the current active ID."""
    registry = service.profiles
    return ProfileListResponse(
        active_id=registry.active_id,
        profiles=[
            ProfileModel(
                id=p.id,
                name=p.name,
                description=p.description,
                system_prompt=p.system_prompt,
                guardrails=p.guardrails,
            )
            for p in registry.list_profiles()
        ],
    )


@app.post("/profiles", status_code=201)
async def create_profile(payload: ProfileModel, service: ServiceDep) -> dict[str, str]:
    """Create a new domain profile with persona and guardrails."""
    profile = Profile(
        id=payload.id,
        name=payload.name,
        description=payload.description,
        system_prompt=payload.system_prompt,
        guardrails=payload.guardrails,
    )
    service.update_profile(profile)
    return {"status": "created", "profile_id": profile.id}


@app.put("/profiles/{profile_id}")
async def update_profile(
    profile_id: str, payload: ProfileModel, service: ServiceDep
) -> dict[str, str]:
    """Update an existing domain profile's persona and guardrails."""
    profile = Profile(
        id=profile_id,
        name=payload.name,
        description=payload.description,
        system_prompt=payload.system_prompt,
        guardrails=payload.guardrails,
    )
    service.update_profile(profile)
    return {"status": "updated", "profile_id": profile.id}


# --- Document Management Endpoints -------------------------------------------


def _resolve_data_dir(settings: Settings, profile_id: str | None = None) -> Path:
    """Resolve directory path for a profile or root data path."""
    if profile_id and profile_id != "default":
        return settings.data_path / profile_id
    return settings.data_path


async def _handle_local_upload(
    file: UploadFile, settings: Settings, profile_id: str | None
) -> UploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")
    target_dir = _resolve_data_dir(settings, profile_id)
    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = target_dir / file.filename

    try:
        content = await file.read()
        file_path.write_bytes(content)
        await run_in_threadpool(ingest_file_to_vector_db, file_path, settings, profile_id)
        return UploadResponse(
            filename=file.filename,
            storage="local",
            storage_type="local",
            status="success",
            message="File saved to local storage and indexed successfully.",
            profile_id=profile_id,
        )
    except Exception as e:
        logger.error("Local file save failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Local save failed: {str(e)}")


def _resolve_content_type(filename: str | None) -> str:
    """Resolve MIME type from filename."""
    if not filename:
        return "application/octet-stream"
    suffix = filename.lower().rsplit(".", 1)[-1]
    if suffix == "pdf":
        return "application/pdf"
    if suffix in ("txt", "md"):
        return "text/plain"
    return "application/octet-stream"


def _get_or_init_s3_service(
    s3_service: S3StorageService | None, settings: Settings
) -> S3StorageService:
    """Get active S3 service or initialize a new one with error handling."""
    if s3_service is not None and s3_service.enabled:
        return s3_service
    try:
        active_s3 = S3StorageService(settings)
    except (ValueError, NoCredentialsError) as err:
        logger.error("AWS credentials missing during S3 upload: %s", err)
        raise HTTPException(
            status_code=400,
            detail="AWS credentials not found or invalid. Please update AWS credentials via the UI Settings.",
        ) from err
    except Exception as err:
        logger.error("Failed to initialize S3 service: %s", err)
        raise HTTPException(
            status_code=400,
            detail=f"S3 storage is not enabled or not configured: {err}. Please update AWS credentials via the UI Settings.",
        ) from err

    if not active_s3.enabled:
        raise HTTPException(
            status_code=400,
            detail="AWS credentials not found or invalid. Please update AWS credentials via the UI Settings.",
        )
    return active_s3


async def _handle_s3_upload(
    file: UploadFile, s3_service: S3StorageService | None, profile_id: str | None
) -> UploadResponse:
    settings = get_settings()
    active_s3 = _get_or_init_s3_service(s3_service, settings)
    content_type = _resolve_content_type(file.filename)
    file_bytes = await file.read()
    key_prefix = f"{profile_id}/" if profile_id and profile_id != "default" else ""
    target_key = f"{key_prefix}{file.filename or 'unknown'}"
    try:
        object_key = await run_in_threadpool(
            active_s3.upload_file,
            file_bytes,
            target_key,
            content_type,
        )
        await run_in_threadpool(
            ingest_bytes_to_vector_db,
            file_bytes,
            file.filename or target_key,
            settings,
            profile_id,
        )
        return UploadResponse(
            filename=object_key,
            storage="s3",
            storage_type="s3",
            status="success",
            message="File uploaded to S3 and indexed successfully.",
            profile_id=profile_id,
        )
    except NoCredentialsError as e:
        logger.error("AWS credentials error during upload: %s", e)
        raise HTTPException(
            status_code=400,
            detail="AWS credentials not found or invalid. Please update AWS credentials via the UI Settings.",
        ) from e
    except Exception as e:
        if "credentials" in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail="AWS credentials not found or invalid. Please update AWS credentials via the UI Settings.",
            ) from e
        logger.error("S3 upload failed: %s", e)
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}") from e



@app.post("/documents/upload")
async def upload_document(
    file: UploadFile,
    storage_type: str | None = None,
    profile_id: str | None = None,
    s3_service: S3ServiceDep = None,
) -> UploadResponse:
    """Upload a document to either local storage or S3 with optional tenant profile isolation."""
    settings = get_settings()
    backend = storage_type or ("s3" if settings.use_s3_storage else "local")
    if backend == "s3":
        return await _handle_s3_upload(file, s3_service, profile_id)
    if backend == "local":
        return await _handle_local_upload(file, settings, profile_id)
    raise HTTPException(status_code=400, detail=f"Invalid storage_type '{backend}'. Must be 'local' or 's3'.")


def _list_local_documents(settings: Settings, profile_id: str | None) -> list[DocumentInfo]:
    target_dir = _resolve_data_dir(settings, profile_id)
    if not target_dir.exists():
        return []
    documents = []
    # If scoped to a tenant profile, only check that folder; otherwise check all data
    paths = target_dir.iterdir() if (profile_id and profile_id != "default") else target_dir.rglob("*")
    for path in sorted(paths):
        if not path.is_file():
            continue
        if path.suffix.lower() in (".pdf", ".txt", ".md"):
            stat = path.stat()
            documents.append(
                DocumentInfo(
                    filename=path.name,
                    size=stat.st_size,
                    last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    profile_id=profile_id or "default",
                )
            )
    return documents


async def _handle_s3_list(s3_service: S3ServiceDep, profile_id: str | None) -> list[DocumentInfo]:
    if not s3_service or not s3_service.enabled:
        raise HTTPException(status_code=400, detail="S3 storage is not enabled or not configured.")
    try:
        files = await run_in_threadpool(s3_service.list_files)
        prefix = f"{profile_id}/" if profile_id and profile_id != "default" else ""
        filtered = [f for f in files if f["filename"].startswith(prefix)] if prefix else files
        return [
            DocumentInfo(
                filename=f["filename"].removeprefix(prefix),
                size=f["size"],
                last_modified=f["last_modified"],
                profile_id=profile_id or "default",
            )
            for f in filtered
        ]
    except Exception as e:
        logger.error("S3 list failed: %s", e)
        raise HTTPException(status_code=500, detail=f"S3 list failed: {str(e)}")


@app.get("/documents")
async def list_documents(
    storage_type: str | None = None,
    profile_id: str | None = None,
    s3_service: S3ServiceDep = None,
) -> DocumentListResponse:
    """List documents from either local storage or S3, optionally scoped by profile."""
    settings = get_settings()
    backend = storage_type or ("s3" if settings.use_s3_storage else "local")

    if backend == "s3":
        docs = await _handle_s3_list(s3_service, profile_id)
        return DocumentListResponse(documents=docs, storage_type="s3")

    if backend == "local":
        docs = _list_local_documents(settings, profile_id)
        return DocumentListResponse(documents=docs, storage_type="local")

    raise HTTPException(status_code=400, detail=f"Invalid storage_type '{backend}'. Must be 'local' or 's3'.")


async def _handle_s3_delete(s3_service: S3ServiceDep, filename: str, profile_id: str | None) -> dict[str, str]:
    if not s3_service or not s3_service.enabled:
        raise HTTPException(status_code=400, detail="S3 storage is not enabled or not configured.")
    key_prefix = f"{profile_id}/" if profile_id and profile_id != "default" else ""
    target_key = f"{key_prefix}{filename}"
    try:
        await run_in_threadpool(s3_service.delete_file, target_key)
        return {"status": "deleted", "filename": filename, "storage_type": "s3", "profile_id": profile_id or "default"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found in S3.")
    except Exception as e:
        logger.error("S3 delete failed: %s", e)
        raise HTTPException(status_code=500, detail=f"S3 delete failed: {str(e)}")


def _handle_local_delete(settings: Settings, filename: str, profile_id: str | None) -> dict[str, str]:
    target_dir = _resolve_data_dir(settings, profile_id)
    file_path = target_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found locally.")
    try:
        file_path.unlink()
        return {"status": "deleted", "filename": filename, "storage_type": "local", "profile_id": profile_id or "default"}
    except Exception as e:
        logger.error("Local file delete failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Local delete failed: {str(e)}")


@app.delete("/documents/{filename}")
async def delete_document(
    filename: str,
    storage_type: str | None = None,
    profile_id: str | None = None,
    s3_service: S3ServiceDep = None,
) -> dict[str, str]:
    """Delete a document from storage for a given profile."""
    settings = get_settings()
    backend = storage_type or ("s3" if settings.use_s3_storage else "local")

    if backend == "s3":
        return await _handle_s3_delete(s3_service, filename, profile_id)

    if backend == "local":
        return _handle_local_delete(settings, filename, profile_id)

    raise HTTPException(status_code=400, detail=f"Invalid storage_type '{backend}'. Must be 'local' or 's3'.")


def _resolve_document_media_type(filename: str) -> str:
    """Resolve accurate MIME media type for document viewing and streaming."""
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix == "pdf":
        return "application/pdf"
    if suffix == "md":
        return "text/markdown; charset=utf-8"
    if suffix == "txt":
        return "text/plain; charset=utf-8"
    return "application/octet-stream"


def _find_local_file(settings: Settings, filename: str, profile_id: str | None = None) -> Path | None:
    """Find a local document file in the profile directory or root data directory."""
    target_dir = _resolve_data_dir(settings, profile_id)
    file_path = target_dir / filename
    if file_path.exists() and file_path.is_file():
        return file_path

    root_file = settings.data_path / filename
    if root_file.exists() and root_file.is_file():
        return root_file

    for match in settings.data_path.rglob(filename):
        if match.is_file():
            return match
    return None


async def _handle_s3_fetch(
    s3_service: S3ServiceDep,
    filename: str,
    profile_id: str | None,
    disposition: str = "attachment",
) -> StreamingResponse:
    if not s3_service or not s3_service.enabled:
        raise HTTPException(status_code=400, detail="S3 storage is not enabled or not configured.")
    key_prefix = f"{profile_id}/" if profile_id and profile_id != "default" else ""
    target_key = f"{key_prefix}{filename}"
    try:
        stream = await run_in_threadpool(s3_service.get_file_stream, target_key)
        media_type = _resolve_document_media_type(filename)
        return StreamingResponse(
            stream,
            media_type=media_type,
            headers={"Content-Disposition": f'{disposition}; filename="{filename}"'},
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found in S3.")
    except Exception as e:
        logger.error("S3 fetch failed: %s", e)
        raise HTTPException(status_code=500, detail=f"S3 fetch failed: {str(e)}")


def _handle_local_fetch(
    settings: Settings,
    filename: str,
    profile_id: str | None,
    disposition: str = "attachment",
) -> FileResponse:
    file_path = _find_local_file(settings, filename, profile_id)
    if not file_path:
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found locally.")

    media_type = _resolve_document_media_type(filename)
    return FileResponse(
        file_path,
        filename=filename,
        media_type=media_type,
        content_disposition_type=disposition,
    )


@app.get("/documents/{filename}/view", response_model=None)
async def view_document(
    filename: str,
    storage_type: str | None = None,
    profile_id: str | None = None,
    s3_service: S3ServiceDep = None,
) -> StreamingResponse | FileResponse:
    """View raw document content inline for preview with accurate MIME types."""
    settings = get_settings()
    backend = storage_type or ("s3" if settings.use_s3_storage else "local")
    if backend == "s3":
        return await _handle_s3_fetch(s3_service, filename, profile_id, disposition="inline")
    if backend == "local":
        return _handle_local_fetch(settings, filename, profile_id, disposition="inline")
    raise HTTPException(status_code=400, detail=f"Invalid storage_type '{backend}'. Must be 'local' or 's3'.")


@app.get("/documents/{filename}/download", response_model=None)
async def download_document(
    filename: str,
    request: Request,
    storage_type: str | None = None,
    profile_id: str | None = None,
    inline: bool = False,
    s3_service: S3ServiceDep = None,
) -> StreamingResponse | FileResponse:
    """Download a document from storage for a given profile."""
    settings = get_settings()
    backend = storage_type or ("s3" if settings.use_s3_storage else "local")
    disposition = (
        "inline"
        if (inline or request.headers.get("sec-fetch-dest") == "iframe")
        else "attachment"
    )
    if backend == "s3":
        return await _handle_s3_fetch(s3_service, filename, profile_id, disposition=disposition)
    if backend == "local":
        return _handle_local_fetch(settings, filename, profile_id, disposition=disposition)
    raise HTTPException(status_code=400, detail=f"Invalid storage_type '{backend}'. Must be 'local' or 's3'.")


class BenchmarkRunRequest(BaseModel):
    """Optional parameters for benchmark evaluation."""

    models: list[str] | None = None
    top_k: int = 5
    num_samples: int = 5


@app.post("/benchmarks/run")
async def run_benchmarks(
    payload: BenchmarkRunRequest | None = None,
) -> dict[str, Any]:
    """Execute embedding model benchmark evaluation and update reports."""
    from .benchmarks.cli import main as run_benchmark_cli

    models = payload.models if (payload and payload.models) else None
    top_k = payload.top_k if payload else 5
    num_samples = payload.num_samples if payload else 5

    cli_args: list[str] = ["--top-k", str(top_k), "--num-samples", str(num_samples)]
    if models:
        cli_args.extend(["--models", *models])

    try:
        exit_code = await run_in_threadpool(run_benchmark_cli, cli_args)
        if exit_code != 0:
            raise HTTPException(status_code=500, detail="Benchmark evaluation failed during execution.")
        return {
            "status": "success",
            "message": "Benchmark evaluation completed successfully and report updated.",
        }
    except Exception as e:
        logger.error("Benchmark run failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Benchmark run error: {str(e)}")



# --- Benchmark Reports Endpoint ---------------------------------------------


@app.get("/benchmarks/report")
async def get_benchmark_report() -> BenchmarkReportResponse:
    """Serve the latest embedding benchmark report for the UI dashboard."""
    report_file = Path("./data/benchmark_report.md")
    results_file = Path("./data/benchmark_results.json")

    if report_file.exists():
        markdown_content = report_file.read_text(encoding="utf-8")
        summary: dict[str, Any] = {}
        if results_file.exists():
            try:
                data = json.loads(results_file.read_text(encoding="utf-8"))
                summary = {
                    "total_models": len(data.get("results", [])),
                    "top_k": data.get("top_k", 5),
                    "timestamp": data.get("timestamp"),
                }
            except Exception as e:
                logger.debug("Could not parse results file: %s", e)
        return BenchmarkReportResponse(
            report_markdown=markdown_content,
            has_results=True,
            available=True,
            summary=summary,
        )

    if results_file.exists():
        try:
            suite_data = json.loads(results_file.read_text(encoding="utf-8"))
            suite = BenchmarkSuiteResult.model_validate(suite_data)
            markdown_content = BenchmarkReporter.generate_markdown_report(suite)
            ranked = BenchmarkReporter.get_ranked_winners(suite)
            top_model = ranked[0][1].model_name if ranked else "N/A"
            winner_dict = {"model_name": top_model, "score": ranked[0][2]} if ranked else None
            top_3 = [{"model_name": r.model_name, "score": sc} for _, r, sc in ranked[:3]]
            return BenchmarkReportResponse(
                report_markdown=markdown_content,
                has_results=True,
                available=True,
                overall_winner=winner_dict,
                top_3_models=top_3,
                summary={
                    "total_models": len(suite.results),
                    "top_winner": top_model,
                    "top_k": suite.top_k,
                    "timestamp": suite.timestamp,
                },
            )
        except Exception as e:
            logger.warning("Could not generate report from benchmark_results.json: %s", e)

    return BenchmarkReportResponse(
        report_markdown="*No benchmark reports found. Run `uv run python -m src.benchmarks.cli` to generate model evaluations.*",
        has_results=False,
        available=False,
        summary={},
    )