"""Tests for Multi-Domain Suggestions, Custom Assistants, Conversation Assistant Binding, and Legal Retrieval."""

from pathlib import Path
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient
from langchain_core.documents import Document

from src.api import app
from src.conversation_store import ConversationStore
from src.graph import RetrievalGraph
from src.profiles import ProfileRegistry, Profile
from src.settings import Settings
from src.vector_store import build_retriever, build_vector_store


def test_suggestions_by_domain_all_four_roles() -> None:
    app_js = Path("src/static/assets/app.js").read_text(encoding="utf-8")

    # Verify all 4 roles exist in both languages in SUGGESTIONS_BY_DOMAIN
    assert "trading:" in app_js
    assert "legal:" in app_js
    assert "medical:" in app_js
    assert "quant:" in app_js

    # Verify specific English questions
    assert "What is the difference between initial and maintenance margin?" in app_js
    assert "What are the contract formation rules under the Hungarian Civil Code (Ptk.)?" in app_js
    assert "What are the primary clinical guidelines for patient data privacy (GDPR / HIPAA)?" in app_js
    assert "How do you calculate Value at Risk (VaR) using historical simulation?" in app_js

    # Verify specific Hungarian questions
    assert "Mi a különbség a kezdeti és a fenntartási letét között?" in app_js
    assert "Mi a magyar polgári törvénykönyv szerződéskötéssel kapcsolatos rendelkezései?" in app_js
    assert "Melyek a klinikai betegadat-kezelés és adatvédelem főbb szabályai?" in app_js
    assert "Hogyan számítható ki a Value at Risk (VaR) történeti szimulációval?" in app_js


def test_conversation_store_assistant_binding(tmp_path: Path) -> None:
    db_file = tmp_path / "test_conv.db"
    store = ConversationStore(db_file)

    # 1. Append turn with custom assistant_id
    store.append_turn("session-1", "What is Ptk?", "Ptk is the Civil Code", assistant_id="legal")
    store.append_turn("session-2", "What is margin?", "Margin is deposit", assistant_id="trading")
    store.append_turn("session-3", "General prompt", "Answer", assistant_id=None)

    convs = store.list_conversations()
    conv_map = {c["id"]: c for c in convs}

    assert conv_map["session-1"]["assistant_id"] == "legal"
    assert conv_map["session-2"]["assistant_id"] == "trading"
    assert conv_map["session-3"]["assistant_id"] == "default"

    # 2. Update session-1 assistant_id on new turn
    store.append_turn("session-1", "Followup", "Answer followup", assistant_id="legal")
    convs_updated = store.list_conversations()
    conv_map_updated = {c["id"]: c for c in convs_updated}
    assert conv_map_updated["session-1"]["assistant_id"] == "legal"


def test_custom_profile_lifecycle_and_delete_protection() -> None:
    from src.api import get_service

    class FakeProfileService:
        def __init__(self) -> None:
            self._profiles = ProfileRegistry(
                profiles=(
                    Profile(id="default", name="Default"),
                    Profile(id="legal", name="Legal"),
                    Profile(id="healthcare", name="Healthcare"),
                    Profile(id="finance", name="Finance"),
                ),
                active_id="default",
            )

        @property
        def profiles(self) -> ProfileRegistry:
            return self._profiles

        def update_profile(self, profile: Profile) -> None:
            self._profiles = self._profiles.add_or_update(profile)

        def delete_profile(self, profile_id: str) -> None:
            self._profiles = self._profiles.remove(profile_id)

    fake_service = FakeProfileService()
    app.dependency_overrides[get_service] = lambda: fake_service
    client = TestClient(app)

    try:
        # 1. Attempting to delete a built-in profile returns 400
        res_del_builtin = client.delete("/profiles/legal")
        assert res_del_builtin.status_code == 400
        assert "Cannot delete built-in profile" in res_del_builtin.json()["detail"]

        res_del_default = client.delete("/profiles/default")
        assert res_del_default.status_code == 400

        # 2. Create a custom assistant profile
        custom_id = "custom_compliance_officer"
        payload = {
            "id": custom_id,
            "name": "Chief Compliance Officer",
            "domain": "legal",
            "description": "Internal compliance review",
            "system_prompt": "You are the CCO. Enforce strict regulatory rules.",
            "guardrails": {"enforce_citations": True, "anonymize_phi": False},
        }
        res_create = client.post("/profiles", json=payload)
        assert res_create.status_code == 201

        # Verify custom profile exists in listing
        res_list = client.get("/profiles")
        assert res_list.status_code == 200
        profile_ids = [p["id"] for p in res_list.json()["profiles"]]
        assert custom_id in profile_ids

        # 3. Delete the custom assistant profile
        res_del_custom = client.delete(f"/profiles/{custom_id}")
        assert res_del_custom.status_code == 200
        assert res_del_custom.json()["status"] == "deleted"

        # Verify custom profile is gone
        res_list_after = client.get("/profiles")
        profile_ids_after = [p["id"] for p in res_list_after.json()["profiles"]]
        assert custom_id not in profile_ids_after
    finally:
        app.dependency_overrides.pop(get_service, None)


def test_legal_retriever_configuration_and_grade_acceptance() -> None:
    settings = Settings()

    # 1. Legal retriever kwargs
    legal_retriever = build_retriever(settings, profile_id="legal")
    search_kwargs = legal_retriever.search_kwargs
    assert search_kwargs.get("k", 0) >= 10
    assert search_kwargs.get("fetch_k", 0) >= 50
    assert search_kwargs.get("filter") == {"domain": "legal"}

    # 2. Graph _grade accepts legal statutory documents directly
    fake_llm = MagicMock()
    fake_retriever = MagicMock()
    graph = RetrievalGraph(fake_llm, fake_retriever, settings)

    doc_ptk = Document(page_content="Ptk statutory section", metadata={"source": "ptk_2013_v.txt", "domain": "legal"})
    state = {
        "question": "Mi a szerződéskötés szabálya?",
        "documents": [doc_ptk],
        "profile_id": "legal",
    }
    grade_result = graph._grade(state)
    assert grade_result == {"relevant": True}
    # fake_llm should NOT even be invoked because statutory docs in legal profile are accepted directly
    fake_llm.assert_not_called()
