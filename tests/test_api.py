"""Tests for the FastAPI interface using a fake service."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.api import app, get_service
from src.models import Answer, RetrievalResult, Source


class FakeService:
    def __init__(self) -> None:
        self.reset_calls: list[str] = []

    def answer(self, question: str, session_id: str) -> Answer:
        return Answer(text="Fake answer", sources=[Source(name="doc.pdf", page=2)])

    def retrieve(self, question: str, session_id: str) -> RetrievalResult:
        return RetrievalResult(standalone_question=question, documents=[])

    def stream_answer(self, question, retrieval, session_id):
        yield "Fake "
        yield "answer"

    def reset_history(self, session_id: str) -> None:
        self.reset_calls.append(session_id)


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


def test_reset_session() -> None:
    response = client.delete("/sessions/abc")
    assert response.status_code == 200
    assert response.json() == {"status": "cleared", "session_id": "abc"}
    assert "abc" in fake_service.reset_calls