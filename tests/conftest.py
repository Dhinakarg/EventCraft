"""Pytest configuration and global fixtures ensuring fast and deterministic test runs."""

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_sleep_globally() -> Generator[MagicMock, None, None]:
    """Ensure time.sleep never delays unit test execution."""
    with patch("time.sleep", return_value=None) as mocked_sleep:
        yield mocked_sleep
