"""Tests for the FastAPI interface using a fake service."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.api import app, get_service
from src.models import Answer, RetrievalResult, Source


class FakeService:
    def __init__(self) -> None:
        self.reset_calls: list[str] = []
        self.deleted: list[str] = []
        self.renamed: list[tuple[str, str]] = []
        self.pinned: list[tuple[str, bool]] = []

    def answer(self, question: str, session_id: str) -> Answer:
        return Answer(text="Fake answer", sources=[Source(name="doc.pdf", page=2)])

    def retrieve(self, question: str, session_id: str) -> RetrievalResult:
        return RetrievalResult(standalone_question=question, documents=[])

    def stream_answer(self, question, retrieval, session_id):
        yield "Fake "
        yield "answer"

    def stream_events(self, question, session_id):
        yield {"type": "status", "stage": "retrieving"}
        yield {"type": "token", "text": "Fake "}
        yield {"type": "token", "text": "answer"}
        yield {
            "type": "done",
            "grounded": True,
            "sources": [{"name": "doc.pdf", "page": 2}],
            "note": None,
        }

    def reset_history(self, session_id: str) -> None:
        self.reset_calls.append(session_id)

    def list_conversations(self, limit: int = 15):
        return [
            {
                "id": "c1",
                "title": "Margin basics",
                "updated_at": "2026-01-01",
                "pinned": True,
            }
        ]

    def get_messages(self, session_id: str):
        return [("human", "What is margin?"), ("ai", "Collateral.")]

    def delete_conversation(self, session_id: str) -> None:
        self.deleted.append(session_id)

    def rename_conversation(self, session_id: str, title: str):
        if session_id == "missing":
            return None
        self.renamed.append((session_id, title))
        return title.strip()

    def set_pinned(self, session_id: str, pinned: bool) -> bool:
        if session_id == "missing":
            return False
        self.pinned.append((session_id, pinned))
        return True


fake_service = FakeService()
app.dependency_overrides[get_service] = lambda: fake_service
client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_index_serves_web_ui() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Futures Trading Assistant" in response.text


def test_chat_returns_answer_and_sources() -> None:
    response = client.post("/chat", json={"question": "What is margin?"})
    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Fake answer"
    assert body["sources"] == [{"name": "doc.pdf", "page": 2}]


def test_chat_rejects_empty_question() -> None:
    response = client.post("/chat", json={"question": ""})
    assert response.status_code == 422


def test_chat_stream_returns_tokens() -> None:
    response = client.post("/chat/stream", json={"question": "q"})
    assert response.status_code == 200
    assert response.text == "Fake answer"


def test_chat_events_streams_progress() -> None:
    import json

    response = client.post("/chat/events", json={"question": "q"})
    assert response.status_code == 200
    events = [json.loads(line) for line in response.text.splitlines() if line]

    assert events[0] == {"type": "status", "stage": "retrieving"}
    tokens = "".join(e["text"] for e in events if e["type"] == "token")
    assert tokens == "Fake answer"
    done = events[-1]
    assert done["type"] == "done"
    assert done["grounded"] is True
    assert done["sources"] == [{"name": "doc.pdf", "page": 2}]


def test_reset_session() -> None:
    response = client.delete("/sessions/abc")
    assert response.status_code == 200
    assert response.json() == {"status": "cleared", "session_id": "abc"}
    assert "abc" in fake_service.reset_calls


def test_list_conversations() -> None:
    response = client.get("/conversations")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "c1",
            "title": "Margin basics",
            "updated_at": "2026-01-01",
            "pinned": True,
        }
    ]


def test_get_conversation_messages() -> None:
    response = client.get("/conversations/c1")
    assert response.status_code == 200
    assert response.json() == [
        {"role": "human", "content": "What is margin?"},
        {"role": "ai", "content": "Collateral."},
    ]


def test_delete_conversation() -> None:
    response = client.delete("/conversations/c1")
    assert response.status_code == 200
    assert response.json() == {"status": "deleted", "conversation_id": "c1"}
    assert "c1" in fake_service.deleted


def test_rename_conversation() -> None:
    response = client.patch("/conversations/c1", json={"title": "  New name  "})
    assert response.status_code == 200
    assert response.json() == {
        "status": "renamed",
        "conversation_id": "c1",
        "title": "New name",
    }
    assert ("c1", "  New name  ") in fake_service.renamed


def test_rename_missing_conversation_returns_404() -> None:
    response = client.patch("/conversations/missing", json={"title": "x"})
    assert response.status_code == 404


def test_pin_conversation() -> None:
    response = client.patch("/conversations/c1/pin", json={"pinned": True})
    assert response.status_code == 200
    assert response.json() == {
        "status": "pinned",
        "conversation_id": "c1",
        "pinned": True,
    }
    assert ("c1", True) in fake_service.pinned


def test_unpin_conversation() -> None:
    response = client.patch("/conversations/c1/pin", json={"pinned": False})
    assert response.status_code == 200
    assert response.json()["status"] == "unpinned"


def test_pin_missing_conversation_returns_404() -> None:
    response = client.patch("/conversations/missing/pin", json={"pinned": True})
    assert response.status_code == 404


def test_config_reports_language_and_readiness() -> None:
    response = client.get("/config")
    assert response.status_code == 200
    body = response.json()
    assert body["language"] == "en"
    assert body["provider"] == "gemini"
    assert body["ready"] is False
    assert body["needs_api_key"] is False


def test_set_api_key_stores_and_builds_service(monkeypatch) -> None:
    import src.api as api

    sentinel = object()
    monkeypatch.setattr(api, "validate_api_key", lambda key, settings: True)
    monkeypatch.setattr(api, "store_api_key", lambda key: None)
    monkeypatch.setattr(api, "ensure_vector_db", lambda settings: True)
    monkeypatch.setattr(api, "build_service", lambda settings, key: sentinel)

    try:
        response = client.post("/config/api-key", json={"api_key": "valid-key"})
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        assert app.state.service is sentinel
        assert app.state.setup_reason is None
    finally:
        app.state.service = None
        app.state.setup_reason = None


def test_set_api_key_rejects_invalid_key(monkeypatch) -> None:
    import src.api as api

    monkeypatch.setattr(api, "validate_api_key", lambda key, settings: False)
    response = client.post("/config/api-key", json={"api_key": "bad-key"})
    assert response.status_code == 401


def test_set_app_name() -> None:
    response = client.post("/config/app-name", json={"app_name": "Custom Trading Desk"})
    assert response.status_code == 200
    assert response.json()["app_name"] == "Custom Trading Desk"

    config_res = client.get("/config")
    assert config_res.status_code == 200
    assert config_res.json()["app_name"] == "Custom Trading Desk"


def test_onboarding_config_success(monkeypatch) -> None:
    import os
    import src.api as api
    from src.settings import get_settings

    sentinel = object()
    monkeypatch.setattr(api, "validate_api_key", lambda key, settings: True)
    monkeypatch.setattr(api, "store_api_key", lambda key: None)
    monkeypatch.setattr(api, "ensure_vector_db", lambda settings: True)
    monkeypatch.setattr(api, "build_service", lambda settings, key: sentinel)
    monkeypatch.setattr(api, "_persist_setup_to_env", lambda s: None)

    try:
        payload = {
            "language": "hu",
            "provider": "gemini",
            "model": "gemini-2.5-flash",
            "use_s3_storage": False,
            "api_key": "valid-api-key",
        }
        response = client.post("/config/onboarding", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["language"] == "hu"
        assert body["provider"] == "gemini"
    finally:
        app.state.service = None
        app.state.setup_reason = None
        os.environ.pop("RAG_LANGUAGE", None)
        os.environ.pop("RAG_LLM_PROVIDER", None)
        os.environ.pop("RAG_USE_S3_STORAGE", None)
        os.environ.pop("RAG_SETUP_COMPLETED", None)
        get_settings.cache_clear()


def test_config_setup_endpoint(monkeypatch) -> None:
    import os
    import src.api as api
    from src.settings import get_settings

    sentinel = object()
    monkeypatch.setattr(api, "validate_api_key", lambda key, settings: True)
    monkeypatch.setattr(api, "store_api_key", lambda key: None)
    monkeypatch.setattr(api, "ensure_vector_db", lambda settings: True)
    monkeypatch.setattr(api, "build_service", lambda settings, key: sentinel)
    monkeypatch.setattr(api, "_persist_setup_to_env", lambda s: None)
    monkeypatch.setattr(api, "_persist_aws_credentials_to_file", lambda a, s: None)

    try:
        payload = {
            "language": "hu",
            "llm_provider": "gemini",
            "model": "gemini-3.5-flash-lite",
            "use_s3_storage": True,
            "aws_access_key_id": "AKIA_MOCK_KEY",
            "aws_secret_access_key": "MOCK_SECRET",
            "aws_region": "eu-central-1",
            "aws_s3_bucket_name": "mock-bucket",
            "api_key": "valid-api-key",
            "app_name": "Test Trader",
        }
        response = client.post("/config/setup", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["setup_required"] is False
        assert body["language"] == "hu"
        assert body["provider"] == "gemini"
        assert body["use_s3_storage"] is True

        cfg_res = client.get("/config")
        assert cfg_res.status_code == 200
        assert "setup_required" in cfg_res.json()
    finally:
        app.state.service = None
        app.state.setup_reason = None
        os.environ.pop("RAG_LANGUAGE", None)
        os.environ.pop("RAG_LLM_PROVIDER", None)
        os.environ.pop("RAG_USE_S3_STORAGE", None)
        os.environ.pop("RAG_SETUP_COMPLETED", None)
        os.environ.pop("RAG_APP_NAME", None)
        get_settings.cache_clear()


def test_upload_document_local(tmp_path, monkeypatch) -> None:
    import src.api as api
    from src.settings import get_settings

    settings = get_settings().model_copy(update={"data_path": tmp_path / "data", "use_s3_storage": False})
    monkeypatch.setattr(api, "get_settings", lambda: settings)
    monkeypatch.setattr(api, "ingest_file_to_vector_db", lambda file_path, s, p: 1)

    file_content = b"Sample document text"
    files = {"file": ("sample.txt", file_content, "text/plain")}
    response = client.post("/documents/upload?storage_type=local", files=files)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["storage"] == "local"
    assert body["filename"] == "sample.txt"


def test_upload_document_s3_success(monkeypatch) -> None:
    from unittest.mock import MagicMock
    import src.api as api
    from src.settings import get_settings

    settings = get_settings().model_copy(update={"use_s3_storage": True})
    monkeypatch.setattr(api, "get_settings", lambda: settings)
    mock_s3 = MagicMock()
    mock_s3.enabled = True
    mock_s3.upload_file.return_value = "sample.txt"
    monkeypatch.setattr(api, "ingest_bytes_to_vector_db", lambda b, f, s, p: 1)

    app.dependency_overrides[api.get_s3_service] = lambda: mock_s3
    try:
        files = {"file": ("sample.txt", b"s3 sample content", "text/plain")}
        response = client.post("/documents/upload", files=files)
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert body["storage"] == "s3"
        assert body["filename"] == "sample.txt"
        assert mock_s3.upload_file.called
    finally:
        app.dependency_overrides.pop(api.get_s3_service, None)


def test_upload_document_s3_no_credentials_error(monkeypatch) -> None:
    from unittest.mock import MagicMock
    from botocore.exceptions import NoCredentialsError
    import src.api as api
    from src.settings import get_settings

    settings = get_settings().model_copy(update={"use_s3_storage": True})
    monkeypatch.setattr(api, "get_settings", lambda: settings)
    mock_s3 = MagicMock()
    mock_s3.enabled = True
    mock_s3.upload_file.side_effect = NoCredentialsError()

    app.dependency_overrides[api.get_s3_service] = lambda: mock_s3
    try:
        files = {"file": ("sample.txt", b"s3 sample content", "text/plain")}
        response = client.post("/documents/upload", files=files)
        assert response.status_code == 400
        assert "AWS credentials not found or invalid" in response.json()["detail"]
    finally:
        app.dependency_overrides.pop(api.get_s3_service, None)


