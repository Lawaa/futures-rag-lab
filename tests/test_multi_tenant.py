"""Tests for multi-tenant and multi-domain RAG platform extensions.

Covers:
- Guardrails (PII/PHI detection and scrubbing)
- Domain Profiles schema and registry
- Vector store collection name isolation
- Prompt generation with guardrail rules
- FastAPI endpoints (profiles, documents, benchmarks)
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src.api import app, get_service
from src.guardrails import (
    apply_guardrails_to_inputs,
    apply_guardrails_to_outputs,
    contains_phi,
    scrub_phi,
)
from src.models import Answer
from src.profiles import Profile, ProfileRegistry, load_profiles
from src.prompts import get_qa_prompt
from src.settings import get_settings
from src.vector_store import get_collection_name


# --- Guardrails Unit Tests ---------------------------------------------------

def test_scrub_phi_ssn() -> None:
    text = "Patient SSN is 123-45-6789, please keep confidential."
    scrubbed = scrub_phi(text)
    assert "123-45-6789" not in scrubbed
    assert "[REDACTED_SSN]" in scrubbed


def test_scrub_phi_email_and_phone() -> None:
    text = "Contact doc@hospital.org or call 555-123-4567 for queries."
    scrubbed = scrub_phi(text)
    assert "doc@hospital.org" not in scrubbed
    assert "[REDACTED_EMAIL]" in scrubbed
    assert "555-123-4567" not in scrubbed
    assert "[REDACTED_PHONE]" in scrubbed


def test_scrub_phi_mrn_and_card() -> None:
    text = "MRN: MRN-98765432 and card 4111-2222-3333-4444 charged."
    scrubbed = scrub_phi(text)
    assert "MRN-98765432" not in scrubbed
    assert "[REDACTED_MRN]" in scrubbed
    assert "4111-2222-3333-4444" not in scrubbed
    assert "[REDACTED_CARD]" in scrubbed


def test_contains_phi() -> None:
    assert contains_phi("User SSN: 000-12-3456") is True
    assert contains_phi("Plain text without any identifiers.") is False


def test_apply_guardrails_to_inputs_and_outputs() -> None:
    guardrails_enabled = {"anonymize_phi": True}
    guardrails_disabled = {"anonymize_phi": False}

    sample = "Call me at 800-555-0199 or email test@example.com"

    # Enabled
    scrubbed_in = apply_guardrails_to_inputs(sample, guardrails_enabled)
    assert "[REDACTED_PHONE]" in scrubbed_in
    assert "[REDACTED_EMAIL]" in scrubbed_in

    scrubbed_out = apply_guardrails_to_outputs(sample, guardrails_enabled)
    assert "[REDACTED_PHONE]" in scrubbed_out

    # Disabled
    clean_in = apply_guardrails_to_inputs(sample, guardrails_disabled)
    assert clean_in == sample


# --- Profile Schema & Registry Tests -----------------------------------------

def test_profile_schema_and_defaults() -> None:
    p = Profile(
        id="finance",
        name="Finance Advisor",
        description="Market and derivative analytics",
        system_prompt="You are a quantitative finance specialist.",
        guardrails={"enforce_citations": True},
    )
    assert p.id == "finance"
    assert p.guardrails.get("enforce_citations") is True


def test_profile_registry_loading() -> None:
    settings = get_settings()
    registry = load_profiles(settings)
    profiles = registry.list_profiles()
    ids = [p.id for p in profiles]

    assert "default" in ids
    assert "legal" in ids
    assert "healthcare" in ids
    assert "finance" in ids

    legal = registry.get("legal")
    assert legal is not None
    assert legal.guardrails.get("enforce_citations") is True

    healthcare = registry.get("healthcare")
    assert healthcare is not None
    assert healthcare.guardrails.get("anonymize_phi") is True


def test_profile_registry_add_or_update() -> None:
    base_profile = Profile(
        id="default",
        name="Default Assistant",
        description="Base profile",
    )
    registry = ProfileRegistry(profiles=[base_profile], active_id="default")
    new_profile = Profile(
        id="custom_tenant",
        name="Custom Tenant",
        description="Special tenant scope",
        system_prompt="Custom instructions",
    )
    updated_registry = registry.add_or_update(new_profile)
    fetched = updated_registry.get("custom_tenant")
    assert fetched is not None
    assert fetched.name == "Custom Tenant"


# --- Vector Store Collection Name Isolation Tests ----------------------------

def test_get_collection_name() -> None:
    assert get_collection_name(None) == "langchain"
    assert get_collection_name("") == "langchain"
    assert get_collection_name("default") == "langchain"
    assert get_collection_name("legal") == "tenant_legal"
    assert get_collection_name("healthcare") == "tenant_healthcare"
    assert get_collection_name("Finance Dept #1") == "tenant_finance_dept__1"


# --- Dynamic Prompts with Guardrails Tests -----------------------------------

def test_prompt_with_citations_guardrail() -> None:
    legal_profile = Profile(
        id="legal",
        name="Legal Counsel",
        description="Legal review",
        system_prompt="You are a senior corporate attorney.",
        guardrails={"enforce_citations": True},
    )
    prompt = get_qa_prompt(
        language="en",
        system_prompt=legal_profile.system_prompt,
        guardrails=legal_profile.guardrails,
    )
    prompt_str = str(prompt)

    assert "senior corporate attorney" in prompt_str
    assert "Mandatory Citation Rules" in prompt_str
    assert "explicitly cited" in prompt_str


def test_prompt_without_citations_guardrail() -> None:
    default_profile = Profile(
        id="default",
        name="Default Assistant",
        description="General assistant",
        system_prompt="You are a helpful assistant.",
        guardrails={"enforce_citations": False},
    )
    prompt = get_qa_prompt(
        language="en",
        system_prompt=default_profile.system_prompt,
        guardrails=default_profile.guardrails,
    )
    prompt_str = str(prompt)

    assert "Mandatory Citation Rules" not in prompt_str


# --- FastAPI Endpoints Tests -------------------------------------------------

class FakeMultiTenantService:
    def __init__(self) -> None:
        self._profiles = load_profiles(get_settings())
        self._settings = get_settings()

    @property
    def profiles(self) -> ProfileRegistry:
        return self._profiles

    def update_profile(self, profile: Profile) -> None:
        self._profiles = self._profiles.add_or_update(profile)

    def answer(self, question: str, session_id: str, profile_id: str | None = None) -> Answer:
        return Answer(text="Tenant answer", sources=[])


@pytest.fixture
def client() -> TestClient:
    fake_service = FakeMultiTenantService()
    app.dependency_overrides[get_service] = lambda: fake_service
    c = TestClient(app)
    yield c
    app.dependency_overrides.pop(get_service, None)


def test_api_get_profiles(client: TestClient) -> None:
    resp = client.get("/profiles")
    assert resp.status_code == 200
    data = resp.json()
    assert "profiles" in data
    ids = [p["id"] for p in data["profiles"]]
    assert "default" in ids
    assert "legal" in ids


def test_api_create_and_update_profile(client: TestClient) -> None:
    new_profile = {
        "id": "compliance_test",
        "name": "Compliance Tester",
        "description": "Test compliance profile",
        "system_prompt": "You are a compliance officer.",
        "guardrails": {"enforce_citations": True, "anonymize_phi": True},
    }
    create_resp = client.post("/profiles", json=new_profile)
    assert create_resp.status_code == 201
    assert create_resp.json()["profile_id"] == "compliance_test"

    updated = dict(new_profile)
    updated["name"] = "Updated Compliance Officer"
    put_resp = client.put("/profiles/compliance_test", json=updated)
    assert put_resp.status_code == 200
    assert put_resp.json()["profile_id"] == "compliance_test"


def test_api_documents_tenant_isolation(client: TestClient, tmp_path: Path) -> None:
    # Query documents for a non-default profile with storage_type=local
    resp = client.get("/documents?storage_type=local&profile_id=test_tenant_xyz")
    assert resp.status_code == 200
    data = resp.json()
    assert "documents" in data
    assert isinstance(data["documents"], list)


def test_api_benchmarks_report(client: TestClient) -> None:
    resp = client.get("/benchmarks/report")
    assert resp.status_code == 200
    data = resp.json()
    assert "available" in data
    assert "report_markdown" in data
