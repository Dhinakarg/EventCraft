"""Input sanitization and untrusted text validation utilities."""

import html
import re

_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]")
_EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
_PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")


def sanitize_text(text: str | None, max_length: int = 1000) -> str:
    """Sanitize and clamp untrusted user text string."""
    if not text:
        return ""
    cleaned = _CONTROL_CHAR_RE.sub("", text)
    cleaned = cleaned.strip()[:max_length]
    return html.escape(cleaned, quote=True)


def sanitize_raw_text(text: str | None, max_length: int = 1000) -> str:
    """Sanitize control chars and clamp length without HTML escaping."""
    if not text:
        return ""
    cleaned = _CONTROL_CHAR_RE.sub("", text)
    return cleaned.strip()[:max_length]


def mask_sensitive_info(text: str) -> str:
    """Mask email addresses and phone numbers to prevent PII leakage."""
    if not text:
        return ""
    masked = _EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    return _PHONE_RE.sub("[REDACTED_PHONE]", masked)
