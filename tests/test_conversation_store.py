"""Tests for the persistent conversation store."""

from __future__ import annotations

from pathlib import Path

from src.conversation_store import ConversationStore


def _store(tmp_path: Path, max_conversations: int = 15) -> ConversationStore:
    return ConversationStore(tmp_path / "conversations.sqlite3", max_conversations)


def test_append_and_load_messages(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.append_turn("c1", "What is margin?", "Collateral.")
    store.append_turn("c1", "And leverage?", "Borrowed exposure.")

    messages = store.load_messages("c1")
    assert messages == [
        ("human", "What is margin?"),
        ("ai", "Collateral."),
        ("human", "And leverage?"),
        ("ai", "Borrowed exposure."),
    ]


def test_title_derived_from_first_question(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.append_turn("c1", "Explain initial margin", "...")
    store.append_turn("c1", "A different follow-up", "...")

    summaries = store.list_conversations()
    assert summaries[0]["id"] == "c1"
    assert summaries[0]["title"] == "Explain initial margin"


def test_list_orders_by_recency(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.append_turn("older", "first", "a")
    store.append_turn("newer", "second", "b")
    store.append_turn("older", "third", "c")  # bumps "older" to the top

    ids = [item["id"] for item in store.list_conversations()]
    assert ids == ["older", "newer"]


def test_prune_keeps_only_max_conversations(tmp_path: Path) -> None:
    store = _store(tmp_path, max_conversations=15)
    for index in range(20):
        store.append_turn(f"c{index}", f"question {index}", "answer")

    summaries = store.list_conversations(limit=100)
    assert len(summaries) == 15
    # The 5 oldest conversations were pruned along with their messages.
    assert store.load_messages("c0") == []
    assert store.load_messages("c19") != []


def test_delete_conversation(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.append_turn("c1", "q", "a")
    store.delete_conversation("c1")

    assert store.list_conversations() == []
    assert store.load_messages("c1") == []


def test_rename_conversation(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.append_turn("c1", "original question", "a")

    result = store.rename_conversation("c1", "  My renamed chat  ")

    assert result == "My renamed chat"
    assert store.list_conversations()[0]["title"] == "My renamed chat"


def test_rename_missing_conversation_returns_none(tmp_path: Path) -> None:
    store = _store(tmp_path)
    assert store.rename_conversation("nope", "title") is None


def test_rename_empty_title_returns_none(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.append_turn("c1", "q", "a")
    assert store.rename_conversation("c1", "   ") is None
    assert store.list_conversations()[0]["title"] == "q"


def test_pinned_conversations_survive_pruning(tmp_path: Path) -> None:
    store = _store(tmp_path, max_conversations=15)
    store.append_turn("keep", "pin me", "a")
    assert store.set_pinned("keep", True) is True

    # Fill well past the retention limit with unpinned conversations.
    for index in range(20):
        store.append_turn(f"c{index}", f"question {index}", "answer")

    ids = {item["id"] for item in store.list_conversations(limit=100)}
    # The pinned conversation is retained even though 20 newer ones exist.
    assert "keep" in ids
    assert store.load_messages("keep") != []
    # Unpinned pool is still capped at the limit (15) plus the pinned one.
    assert len(ids) == 16


def test_list_puts_pinned_first_and_reports_state(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.append_turn("a", "first", "x")
    store.append_turn("b", "second", "y")  # more recent
    store.set_pinned("a", True)

    summaries = store.list_conversations()
    assert summaries[0]["id"] == "a"
    assert summaries[0]["pinned"] is True
    assert summaries[1]["id"] == "b"
    assert summaries[1]["pinned"] is False


def test_unpin_allows_pruning_again(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.append_turn("c1", "q", "a")
    assert store.set_pinned("c1", True) is True
    assert store.set_pinned("c1", False) is True

    summary = store.list_conversations()[0]
    assert summary["pinned"] is False


def test_set_pinned_missing_conversation_returns_false(tmp_path: Path) -> None:
    store = _store(tmp_path)
    assert store.set_pinned("nope", True) is False
