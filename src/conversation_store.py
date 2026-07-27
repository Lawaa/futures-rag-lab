"""Persistent conversation storage backed by SQLite.

Keeps the most recent conversations so users can leave and resume chats, list
past conversations, and delete old ones. Uses only the Python standard library
(``sqlite3``) - no extra dependencies - and opens a fresh connection per call so
it is safe to use from FastAPI's threadpool.
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

# How many of the most recent conversations to retain.
DEFAULT_MAX_CONVERSATIONS = 15

# Characters kept from a conversation title.
_TITLE_MAX_LENGTH = 60


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_title(text: str) -> str:
    """Collapse whitespace and truncate a title; ``""`` when effectively empty."""
    title = " ".join(text.split())
    if len(title) > _TITLE_MAX_LENGTH:
        title = title[: _TITLE_MAX_LENGTH - 1].rstrip() + "…"
    return title


def _derive_title(question: str) -> str:
    return _clean_title(question) or "Untitled"


class ConversationStore:
    """Store and retrieve conversations, keeping only the most recent ones."""

    def __init__(
        self, db_file: Path, max_conversations: int = DEFAULT_MAX_CONVERSATIONS
    ) -> None:
        self._db_file = Path(db_file)
        self._max_conversations = max_conversations
        self._db_file.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()
        self._restrict_permissions()

    # -- setup ----------------------------------------------------------------
    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._db_file)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.row_factory = sqlite3.Row
        return connection

    def _restrict_permissions(self) -> None:
        """Best-effort: make the history readable/writable by the owner only.

        On POSIX systems this tightens the SQLite files to ``0600`` (and the
        containing directory to ``0700``) so other local users cannot read saved
        conversations. Silently ignored where ``chmod`` is unsupported (Windows).
        """
        try:
            os.chmod(self._db_file.parent, 0o700)
        except OSError:
            pass
        for suffix in ("", "-wal", "-shm", "-journal"):
            path = self._db_file.with_name(self._db_file.name + suffix)
            try:
                if path.exists():
                    os.chmod(path, 0o600)
            except OSError:
                pass

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id         TEXT PRIMARY KEY,
                    title      TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    pinned     INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS messages (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role            TEXT NOT NULL,
                    content         TEXT NOT NULL,
                    created_at      TEXT NOT NULL,
                    FOREIGN KEY (conversation_id)
                        REFERENCES conversations (id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_messages_conversation
                    ON messages (conversation_id, id);
                """
            )
            self._migrate(connection)

    def _migrate(self, connection: sqlite3.Connection) -> None:
        """Apply forward-compatible schema tweaks to pre-existing databases."""
        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(conversations)")
        }
        if "pinned" not in columns:
            connection.execute(
                "ALTER TABLE conversations ADD COLUMN pinned INTEGER NOT NULL "
                "DEFAULT 0"
            )

    # -- writes ---------------------------------------------------------------
    def append_turn(self, conversation_id: str, question: str, answer: str) -> None:
        """Append a user question and assistant answer to a conversation.

        Creates the conversation (titled from the first question) if it is new,
        refreshes its ``updated_at`` timestamp, and prunes old conversations.
        """
        timestamp = _now()
        with self._connect() as connection:
            exists = connection.execute(
                "SELECT 1 FROM conversations WHERE id = ?", (conversation_id,)
            ).fetchone()

            if exists is None:
                connection.execute(
                    "INSERT INTO conversations (id, title, created_at, updated_at) "
                    "VALUES (?, ?, ?, ?)",
                    (conversation_id, _derive_title(question), timestamp, timestamp),
                )
            else:
                connection.execute(
                    "UPDATE conversations SET updated_at = ? WHERE id = ?",
                    (timestamp, conversation_id),
                )

            connection.executemany(
                "INSERT INTO messages (conversation_id, role, content, created_at) "
                "VALUES (?, ?, ?, ?)",
                [
                    (conversation_id, "human", question, timestamp),
                    (conversation_id, "ai", answer, timestamp),
                ],
            )
            self._prune(connection)

    def delete_conversation(self, conversation_id: str) -> None:
        """Remove a conversation and all of its messages."""
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM messages WHERE conversation_id = ?", (conversation_id,)
            )
            connection.execute(
                "DELETE FROM conversations WHERE id = ?", (conversation_id,)
            )

    def rename_conversation(self, conversation_id: str, title: str) -> str | None:
        """Rename a conversation.

        Returns the stored (cleaned) title, or ``None`` when the conversation
        does not exist or the requested title is empty.
        """
        clean = _clean_title(title)
        if not clean:
            return None
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE conversations SET title = ? WHERE id = ?",
                (clean, conversation_id),
            )
        return clean if cursor.rowcount > 0 else None

    def set_pinned(self, conversation_id: str, pinned: bool) -> bool:
        """Pin or unpin a conversation.

        Pinned conversations are exempt from automatic pruning, so they survive
        beyond the ``max_conversations`` retention limit. Returns ``True`` when a
        conversation was updated, ``False`` when it does not exist.
        """
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE conversations SET pinned = ? WHERE id = ?",
                (1 if pinned else 0, conversation_id),
            )
        return cursor.rowcount > 0

    def _prune(self, connection: sqlite3.Connection) -> None:
        """Keep only the ``max_conversations`` most recent *unpinned* chats.

        Pinned conversations are never pruned and do not count against the limit.
        """
        stale = connection.execute(
            "SELECT id FROM conversations WHERE pinned = 0 "
            "ORDER BY updated_at DESC, id DESC LIMIT -1 OFFSET ?",
            (self._max_conversations,),
        ).fetchall()
        for row in stale:
            connection.execute(
                "DELETE FROM messages WHERE conversation_id = ?", (row["id"],)
            )
            connection.execute(
                "DELETE FROM conversations WHERE id = ?", (row["id"],)
            )

    # -- reads ----------------------------------------------------------------
    def list_conversations(
        self, limit: int = DEFAULT_MAX_CONVERSATIONS
    ) -> list[dict]:
        """Return recent conversations, pinned first then most recently updated."""
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, title, updated_at, pinned FROM conversations "
                "ORDER BY pinned DESC, updated_at DESC, id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {
                "id": row["id"],
                "title": row["title"],
                "updated_at": row["updated_at"],
                "pinned": bool(row["pinned"]),
            }
            for row in rows
        ]

    def load_messages(self, conversation_id: str) -> list[tuple[str, str]]:
        """Return the ordered ``(role, content)`` pairs for a conversation."""
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT role, content FROM messages "
                "WHERE conversation_id = ? ORDER BY id",
                (conversation_id,),
            ).fetchall()
        return [(row["role"], row["content"]) for row in rows]
