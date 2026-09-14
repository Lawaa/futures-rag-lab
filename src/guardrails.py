"""Domain guardrails and data privacy sanitizers.

Provides zero-external-dependency PII/PHI scrubbers and compliance validators.
"""

from __future__ import annotations

import re
from typing import Any

# Regular expressions for common Personally Identifiable Information (PII)
# and Protected Health Information (PHI)
_PATTERNS: dict[str, re.Pattern[str]] = {
    "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "MRN": re.compile(r"\b(?:MRN|mrn|Medical Record(?:\s*Number)?)[:\s#\-]*[A-Za-z0-9\-]{6,16}\b", re.IGNORECASE),
    "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "PHONE": re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "DOB": re.compile(r"\b(?:DOB|dob|Date of Birth)[:\s#\-]*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", re.IGNORECASE),
    "CREDIT_CARD": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
}


def scrub_phi(text: str) -> str:
    """Redact sensitive PII/PHI patterns from text.

    Replaces Social Security Numbers, Medical Record Numbers, phone numbers,
    emails, dates of birth, and credit card numbers with standardized redaction tokens.
    """
    if not text:
        return text

    sanitized = text

    # SSN
    sanitized = _PATTERNS["SSN"].sub("[REDACTED_SSN]", sanitized)
    # Credit Card
    sanitized = _PATTERNS["CREDIT_CARD"].sub("[REDACTED_CARD]", sanitized)
    # MRN
    sanitized = _PATTERNS["MRN"].sub("[REDACTED_MRN]", sanitized)
    # DOB
    sanitized = _PATTERNS["DOB"].sub("[REDACTED_DOB]", sanitized)
    # Email
    sanitized = _PATTERNS["EMAIL"].sub("[REDACTED_EMAIL]", sanitized)
    # Phone
    sanitized = _PATTERNS["PHONE"].sub("[REDACTED_PHONE]", sanitized)

    return sanitized


def contains_phi(text: str) -> bool:
    """Check if text contains any recognized PII/PHI patterns."""
    if not text:
        return False
    return any(pattern.search(text) is not None for pattern in _PATTERNS.values())


def apply_guardrails_to_inputs(text: str, guardrails: dict[str, Any] | None) -> str:
    """Apply active domain input guardrails (e.g. PHI scrubbing)."""
    if not guardrails or not text:
        return text

    if guardrails.get("anonymize_phi", False):
        return scrub_phi(text)

    return text


def apply_guardrails_to_outputs(text: str, guardrails: dict[str, Any] | None) -> str:
    """Apply active domain output guardrails (e.g. PHI scrubbing)."""
    if not guardrails or not text:
        return text

    if guardrails.get("anonymize_phi", False):
        return scrub_phi(text)

    return text
