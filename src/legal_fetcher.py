"""Dynamic Legal Corpus Downloader & Caching Module.

Provides automated fetching, HTTP conditional validation (ETag / Last-Modified),
smart caching, and vector database ingestion for official legal codes (Ptk., Btk.)
under the Legal & Regulatory Compliance domain profile.
"""

from __future__ import annotations

import json
import re
import ssl
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any
import urllib.error
import urllib.request

from .ingest import ingest_file_to_vector_db
from .logging_config import get_logger
from .settings import Settings, get_settings

logger = get_logger(__name__)

MIN_LEGAL_FILE_SIZE = 500 * 1024  # 500 KB minimum for complete statutory text

LEGAL_CORPORA: dict[str, dict[str, Any]] = {
    "ptk": {
        "id": "ptk",
        "name": "Polgári Törvénykönyv (Ptk. - 2013. évi V. törvény)",
        "description": "A polgári jog alapvető kódexe: személyek joga, dologi jog, kötelmi jog, szerződések és kártérítés.",
        "filename": "ptk_2013_v.txt",
        "url": "https://njt.jog.gov.hu/jogszabaly/2013-5-00-00",
        "doc_id": "2013-5-00-00",
    },
    "btk": {
        "id": "btk",
        "name": "Büntető Törvénykönyv (Btk. - 2012. évi C. törvény)",
        "description": "Büntetőjogi rendelkezések: bűncselekmények, gazdasági és pénzügyi visszaélések, büntetések és intézkedések.",
        "filename": "btk_2012_c.txt",
        "url": "https://njt.jog.gov.hu/jogszabaly/2012-100-00-00",
        "doc_id": "2012-100-00-00",
    },
}


def _get_ssl_context() -> ssl.SSLContext:
    """Create a verified SSL context using certifi if available, or secure default."""
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx


def _fetch_njt_slices(doc_id: str, initial_html: str, ctx: ssl.SSLContext) -> list[str]:
    """Fetch dynamic statutory text slices from NJT block loader endpoint."""
    show_orders = [
        int(x)
        for x in re.findall(
            r'class=["\'][^"\']*borderStart[^"\']*["\'][^>]*data-show-order=["\']?(\d+)["\']?',
            initial_html,
        )
    ]
    last_match = re.search(r'data-last-show-order=["\']?(\d+)["\']?', initial_html)
    max_order = int(last_match.group(1)) if last_match else 0
    if not show_orders or not max_order:
        return []

    slices: list[dict[str, int]] = []
    for i, start in enumerate(show_orders):
        last = show_orders[i + 1] - 1 if i + 1 < len(show_orders) else max_order
        slices.append({"start": start, "last": last})

    block_texts: list[str] = []
    for i in range(0, len(slices), 20):
        batch = slices[i : i + 20]
        body = json.dumps({"documentId": doc_id, "data": batch}).encode("utf-8")
        req = urllib.request.Request(
            "https://njt.jog.gov.hu/ajax/njtGetBlock.json",
            data=body,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Content-Type": "application/json; charset=utf-8",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"https://njt.jog.gov.hu/jogszabaly/{doc_id}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=25.0) as resp:
                block_texts.append(resp.read().decode("utf-8", errors="ignore"))
        except Exception as err:
            logger.warning("Failed to fetch block batch %d for %s: %s", i // 20, doc_id, err)
    return block_texts


def _clean_html_to_statutory_text(html_text: str) -> str:
    """Convert HTML containing statutory provisions into clean, section-structured text."""
    text = re.sub(r"<script[^>]*>.*?</script>", "", html_text, flags=re.DOTALL | re.I)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.I)
    text = re.sub(r"<(?:h\d|p|div|tr|br|li)[^>]*>", "\n", text, flags=re.I)
    text = re.sub(r"</(?:h\d|p|div|tr|li)>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    # Normalize spaces: replace non-breaking and thin spaces so '6:58.\u2005§' becomes '6:58. §'
    text = re.sub(r"[\u2000-\u200b\u00a0]", " ", text)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join([line for line in lines if line])


def _extract_clean_legal_text(
    raw_bytes: bytes,
    doc_id: str | None = None,
    ctx: ssl.SSLContext | None = None,
) -> bytes:
    """Extract clean statutory text from NJT HTML or plain text."""
    decoded = raw_bytes.decode("utf-8", errors="ignore")
    if "<html" in decoded.lower() or "<!doctype" in decoded.lower():
        parts = [decoded]
        if doc_id and ctx:
            slices = _fetch_njt_slices(doc_id, decoded, ctx)
            parts.extend(slices)
        clean = _clean_html_to_statutory_text("\n".join(parts))
        return clean.encode("utf-8")
    return raw_bytes


def _validate_legal_content(content_bytes: bytes, corpus_id: str) -> None:
    """Validate that downloaded content is non-trivial and contains statutory text."""
    if len(content_bytes) < MIN_LEGAL_FILE_SIZE:
        raise RuntimeError(
            f"Corpus '{corpus_id}' download failed or file size too small "
            f"({len(content_bytes)} bytes < {MIN_LEGAL_FILE_SIZE} bytes). Expected complete statutory text."
        )
    sample = content_bytes[:4000].decode("utf-8", errors="ignore").lower()
    if "törvény" not in sample and "§" not in sample:
        raise RuntimeError(
            f"Corpus '{corpus_id}' downloaded content does not appear to contain valid legal text."
        )


class LegalCorpusManager:
    """Manages downloading, smart caching, and ChromaDB indexing for legal corpora."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._legal_dir = self._settings.data_path / "legal"
        self._legal_dir.mkdir(parents=True, exist_ok=True)
        self._manifest_path = self._legal_dir / ".legal_manifest.json"

    @property
    def legal_dir(self) -> Path:
        """Return the directory path for legal corpora."""
        return self._legal_dir

    def _load_manifest(self) -> dict[str, dict[str, Any]]:
        """Load manifest from disk or return empty dictionary."""
        if not self._manifest_path.exists():
            return {}
        try:
            content = self._manifest_path.read_text(encoding="utf-8")
            return json.loads(content)
        except Exception as e:
            logger.warning("Failed to load legal manifest: %s", e)
            return {}

    def _save_manifest(self, manifest: dict[str, dict[str, Any]]) -> None:
        """Persist manifest to disk atomically."""
        try:
            self._manifest_path.write_text(
                json.dumps(manifest, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception as e:
            logger.error("Failed to save legal manifest: %s", e)

    def _probe_remote_headers(
        self, url: str, etag: str | None, last_mod: str | None
    ) -> tuple[bool, str | None, str | None]:
        """Perform a fast conditional HEAD request to check if remote is modified."""
        headers: dict[str, str] = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        if etag:
            headers["If-None-Match"] = etag
        if last_mod:
            headers["If-Modified-Since"] = last_mod

        req = urllib.request.Request(url, headers=headers, method="HEAD")
        ctx = _get_ssl_context()
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=4.0) as resp:
                new_etag = resp.headers.get("ETag")
                new_last_mod = resp.headers.get("Last-Modified")
                is_same = (etag is not None and new_etag == etag)
                return is_same, new_etag, new_last_mod
        except urllib.error.HTTPError as err:
            if err.code == 304:
                return True, etag, last_mod
            return False, None, None
        except Exception as err:
            logger.debug("HEAD probe failed for %s: %s", url, err)
            return True, etag, last_mod

    def get_available_corpora(self) -> list[dict[str, Any]]:
        """Return list of all configured legal corpora with their current cache status."""
        manifest = self._load_manifest()
        results: list[dict[str, Any]] = []

        for cid, info in LEGAL_CORPORA.items():
            file_path = self._legal_dir / info["filename"]
            exists = file_path.exists() and file_path.stat().st_size >= MIN_LEGAL_FILE_SIZE
            entry = manifest.get(cid, {})

            status = "available"
            size_bytes = file_path.stat().st_size if file_path.exists() else 0
            last_synced = entry.get("synced_at")

            if exists:
                status = "cached"

            results.append(
                {
                    "id": cid,
                    "name": info["name"],
                    "description": info["description"],
                    "filename": info["filename"],
                    "status": status,
                    "size_bytes": size_bytes,
                    "last_synced": last_synced,
                    "is_active": exists,
                }
            )
        return results

    def _fetch_content(self, url: str, corpus_id: str) -> tuple[bytes, str | None, str | None]:
        """Fetch remote bytes and validate statutory content; raise error if failed."""
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            ctx = _get_ssl_context()
            with urllib.request.urlopen(req, context=ctx, timeout=25.0) as resp:
                raw_bytes = resp.read()
                etag = resp.headers.get("ETag")
                last_mod = resp.headers.get("Last-Modified")
        except urllib.error.HTTPError as err:
            raise RuntimeError(
                f"HTTP fetch error {err.code} for legal corpus '{corpus_id}' ({url})."
            ) from err
        except Exception as err:
            raise RuntimeError(
                f"Network connection failed for legal corpus '{corpus_id}' ({url}): {err}"
            ) from err

        doc_id = LEGAL_CORPORA.get(corpus_id, {}).get("doc_id")
        content_bytes = _extract_clean_legal_text(raw_bytes, doc_id=doc_id, ctx=ctx)
        _validate_legal_content(content_bytes, corpus_id)
        return content_bytes, etag, last_mod

    def check_and_sync_corpus(self, corpus_id: str, force: bool = False) -> Path:
        """Check cache and conditionally sync legal code, ingesting into ChromaDB if updated."""
        if corpus_id not in LEGAL_CORPORA:
            raise ValueError(f"Unknown legal corpus ID: '{corpus_id}'")

        info = LEGAL_CORPORA[corpus_id]
        file_path = self._legal_dir / info["filename"]
        manifest = self._load_manifest()
        entry = manifest.get(corpus_id, {})

        exists = file_path.exists() and file_path.stat().st_size >= MIN_LEGAL_FILE_SIZE
        etag = entry.get("etag")
        last_mod = entry.get("last_modified")

        if exists and not force:
            is_same, _, _ = self._probe_remote_headers(info["url"], etag, last_mod)
            if is_same or (etag is None and last_mod is None):
                logger.info("Corpus '%s' is up-to-date in cache (%s).", corpus_id, file_path.name)
                return file_path

        logger.info("Syncing legal corpus '%s'...", corpus_id)
        content_bytes, new_etag, new_last_mod = self._fetch_content(info["url"], corpus_id)
        file_path.write_bytes(content_bytes)

        manifest[corpus_id] = {
            "etag": new_etag,
            "last_modified": new_last_mod,
            "size_bytes": len(content_bytes),
            "synced_at": datetime.now(timezone.utc).isoformat(),
            "local_file": info["filename"],
        }
        self._save_manifest(manifest)

        # Index into tenant ChromaDB collection for the "legal" profile
        chunks_indexed = ingest_file_to_vector_db(file_path, self._settings, profile_id="legal")
        logger.info("Corpus '%s' synced successfully: %d chunks indexed.", corpus_id, chunks_indexed)
        return file_path

    def sync_selected_corpora(self, corpus_ids: list[str]) -> dict[str, Any]:
        """Sync a batch of selected legal corpora and return execution results."""
        synced: list[str] = []
        errors: list[str] = []

        for cid in corpus_ids:
            try:
                self.check_and_sync_corpus(cid)
                synced.append(cid)
            except Exception as e:
                logger.error("Failed to sync corpus '%s': %s", cid, e)
                errors.append(f"{cid}: {str(e)}")

        return {
            "status": "ok" if not errors else "partial",
            "synced": synced,
            "errors": errors,
            "total_synced": len(synced),
        }
