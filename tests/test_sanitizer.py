"""Unit tests for input sanitization, untrusted text validation, and PII protection."""

from datetime import date, timedelta

import pytest

from app.sanitizer import (
    mask_sensitive_info,
    sanitize_raw_text,
    sanitize_text,
    validate_future_date,
    validate_priorities,
)


def test_sanitize_text_strips_control_characters() -> None:
    """Test removing control characters and limiting length."""
    raw = "Hello\x00\x08World\x1f!"
    cleaned = sanitize_text(raw, max_length=10)
    assert cleaned == "HelloWorld"


def test_sanitize_text_escapes_html() -> None:
    """Test escaping dangerous HTML characters."""
    bad_input = "<script>alert('xss')</script>"
    safe_output = sanitize_text(bad_input)
    assert "<script>" not in safe_output
    assert "&lt;script&gt;" in safe_output


def test_sanitize_raw_text_no_escape() -> None:
    """Test raw sanitation strips control chars without html entity conversion."""
    raw = "Dinner & Dancing\x00"
    cleaned = sanitize_raw_text(raw, max_length=50)
    assert cleaned == "Dinner & Dancing"


def test_mask_sensitive_info_email() -> None:
    """Test email address masking for zero PII leakage."""
    text = "Contact me at alice.smith@example.com for booking"
    masked = mask_sensitive_info(text)
    assert "alice.smith@example.com" not in masked
    assert "[REDACTED_EMAIL]" in masked


def test_mask_sensitive_info_phone() -> None:
    """Test phone number masking for zero PII leakage."""
    text = "Call coordinator at +1-555-123-4567 or 555-987-6543."
    masked = mask_sensitive_info(text)
    assert "555-123-4567" not in masked
    assert "[REDACTED_PHONE]" in masked


def test_validate_future_date() -> None:
    """Test future date validator allows future dates and rejects past/today dates."""
    future = date.today() + timedelta(days=10)
    assert validate_future_date(future) == future

    past = date.today() - timedelta(days=1)
    with pytest.raises(ValueError, match="event_date must be in the future"):
        validate_future_date(past)

    with pytest.raises(ValueError, match="event_date must be in the future"):
        validate_future_date(date.today())


def test_validate_priorities() -> None:
    """Test priority validator validates, deduplicates, and rejects invalid options."""
    valid = ["venue", "food"]
    assert validate_priorities(valid) == ["venue", "food"]

    with pytest.raises(ValueError, match="priorities cannot exceed 3 items"):
        validate_priorities(["venue", "food", "decor", "entertainment"])

    with pytest.raises(ValueError, match="Invalid priority"):
        validate_priorities(["invalid_category"])
