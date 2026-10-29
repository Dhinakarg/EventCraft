"""Centralized named constants, limits, thresholds, and default configurations."""

# Guest Count Limits
MIN_GUEST_COUNT = 1
MAX_GUEST_COUNT = 2000

# String Field Length Limits
MAX_CITY_LENGTH = 100
MAX_VIBE_LENGTH = 80
MAX_NOTES_LENGTH = 500
MAX_PRIORITIES_COUNT = 3
VALID_PRIORITIES = {"venue", "food", "decor", "photography", "entertainment", "other"}
MAX_CHAT_QUESTION_LENGTH = 300
MAX_CHAT_REPLY_LENGTH = 400

# Cache and Network Retry Settings
DEFAULT_CACHE_MAX_SIZE = 128
DEFAULT_RETRY_ATTEMPTS = 2
DEFAULT_TIMEOUT_MS = 10_000

# Budget and Financial Allocation Thresholds
PRIORITY_BOOST_MULTIPLIER = 1.25
DEFAULT_CONTINGENCY_RATE = 10.0
MIN_CONTINGENCY_RATE = 5.0
MAX_CONTINGENCY_RATE = 20.0
DEFAULT_VENDOR_BUDGET_RATIO = 0.15
