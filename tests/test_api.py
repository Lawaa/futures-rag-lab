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
