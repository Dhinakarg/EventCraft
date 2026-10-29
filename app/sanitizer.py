"""Input sanitization, untrusted text validation, and PII protection utilities."""

import html
import re
from datetime import date

from app.constants import (
    MAX_PRIORITIES_COUNT,
    VALID_PRIORITIES,
)

_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]")
_EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
_PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")


def sanitize_text(text: str | None, max_length: int = 1000, escape_html: bool = True) -> str:
    """Sanitize control chars and clamp untrusted user text, optionally escaping HTML."""
    if not text:
        return ""
    cleaned = _CONTROL_CHAR_RE.sub("", text).strip()[:max_length]
    if escape_html:
        return html.escape(cleaned, quote=True)
    return cleaned


def sanitize_raw_text(text: str | None, max_length: int = 1000) -> str:
    """Sanitize control chars and clamp length without HTML escaping."""
    return sanitize_text(text, max_length=max_length, escape_html=False)


def mask_sensitive_info(text: str) -> str:
    """Mask email addresses and phone numbers to prevent PII leakage."""
    if not text:
        return ""
    masked = _EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    return _PHONE_RE.sub("[REDACTED_PHONE]", masked)


def validate_future_date(v: date) -> date:
    """Ensure the event date is set strictly in the future."""
    if v <= date.today():
        raise ValueError("event_date must be in the future")
    return v


def validate_priorities(v: list[str]) -> list[str]:
    """Validate maximum priorities from the allowed set."""
    if len(v) > MAX_PRIORITIES_COUNT:
        raise ValueError(f"priorities cannot exceed {MAX_PRIORITIES_COUNT} items")
    cleaned: list[str] = []
    for p in v:
        norm = p.strip().lower()
        if norm not in VALID_PRIORITIES:
            msg = f"Invalid priority '{p}'. Must be one of {sorted(VALID_PRIORITIES)}"
            raise ValueError(msg)
        if norm not in cleaned:
            cleaned.append(norm)
    return cleaned
