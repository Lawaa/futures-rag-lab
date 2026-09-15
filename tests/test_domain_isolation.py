"""Tests for strict domain metadata tagging, Knowledge Base isolation, and RAG domain filtering."""

from pathlib import Path
from unittest.mock import MagicMock
from langchain_core.documents import Document

from src.api import _list_local_documents, DocumentInfo
from src.graph import _filter_legal_documents, _is_ptk, _is_btk
from src.ingest import resolve_domain
from src.settings import Settings


def test_resolve_domain_tagging() -> None:
    assert resolve_domain("default", "cme_futures.pdf") == "trading"
    assert resolve_domain("trading", "energy_rules.txt") == "trading"
    assert resolve_domain("legal", "custom_law.pdf") == "legal"
    assert resolve_domain(None, "ptk_2013_v.txt") == "legal"
    assert resolve_domain(None, "btk_2012_c.txt") == "legal"
    assert resolve_domain("default", "law.txt", Path("data/legal/law.txt")) == "legal"
    assert resolve_domain("healthcare", "clinical.pdf") == "healthcare"


def test_list_local_documents_trading_mode_excludes_legal(tmp_path: Path) -> None:
    # Setup mock data directory
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    legal_dir = data_dir / "legal"
    legal_dir.mkdir(parents=True)

    # Create trading and legal documents
    (data_dir / "futures_contracts.pdf").write_text("trading content", encoding="utf-8")
    (data_dir / "margin_rules.txt").write_text("margin content", encoding="utf-8")
    (legal_dir / "ptk_2013_v.txt").write_text("ptk content", encoding="utf-8")
    (legal_dir / "btk_2012_c.txt").write_text("btk content", encoding="utf-8")

    settings = Settings(data_path=data_dir)

    # 1. Trading / default profile should ONLY list trading documents
    trading_docs = _list_local_documents(settings, profile_id="default")
    trading_names = [d.filename for d in trading_docs]
    assert "futures_contracts.pdf" in trading_names
    assert "margin_rules.txt" in trading_names
    assert "ptk_2013_v.txt" not in trading_names
    assert "btk_2012_c.txt" not in trading_names
    for doc in trading_docs:
        assert doc.domain == "trading"

    # 2. Legal profile should list legal documents
    legal_docs = _list_local_documents(settings, profile_id="legal")
    legal_names = [d.filename for d in legal_docs]
    assert "ptk_2013_v.txt" in legal_names
    assert "btk_2012_c.txt" in legal_names
    assert "futures_contracts.pdf" not in legal_names
    for doc in legal_docs:
        assert doc.domain == "legal"


def test_graph_legal_helpers() -> None:
    doc_ptk = Document(page_content="Ptk text", metadata={"source": "ptk_2013_v.txt", "domain": "legal"})
    doc_btk = Document(page_content="Btk text", metadata={"source": "btk_2012_c.txt", "domain": "legal"})
    doc_trade = Document(page_content="Futures text", metadata={"source": "cme.pdf", "domain": "trading"})

    assert _is_ptk(doc_ptk) is True
    assert _is_ptk(doc_trade) is False
    assert _is_btk(doc_btk) is True
    assert _is_btk(doc_trade) is False


def test_ui_scrollbar_and_tooltip_localization() -> None:
    app_css = Path("src/static/assets/app.css").read_text(encoding="utf-8")
    app_js = Path("src/static/assets/app.js").read_text(encoding="utf-8")
    index_html = Path("src/static/index.html").read_text(encoding="utf-8")

    # Custom scrollbar exists in CSS
    assert ".custom-scrollbar" in app_css
    assert "::-webkit-scrollbar" in app_css
    assert "scrollbar-width: thin;" in app_css

    # Törvénytár hidden initially
    assert 'id="nav-legal" type="button" style="display: none;"' in index_html

    # Tooltip translation keys exist in JS
    assert "ttThemeToggle" in app_js
    assert "ttInspectorToggle" in app_js
    assert "ttViewFullDoc" in app_js
    assert "Téma váltása (Sötét / Világos)" in app_js
    assert "Dokumentum Vizsgáló panel megnyitása/elrejtése" in app_js

    # data-i18n-title handler present in applyLanguage
    assert 'document.querySelectorAll("[data-i18n-title]")' in app_js
