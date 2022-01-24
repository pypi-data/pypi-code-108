POOL_CONNECTIONS = 10
"""The number of connection pools to cache."""

POOL_MAXSIZE = 10
"""Max connections to a host for a connection pool. (Only matters for concurrency)."""

REQUESTS_TIMEOUT = 60
"""Default timeout for connection attempts."""

RETRIES = 4
"""Number of attempts to retry connection failures."""

RETRY_BACKOFF = 1.0
"""
Default backoff factor for retries.

The requests library uses `b * (2 ** (i - 1))` where b is the backoff factor (this value) and i is the retry
number.
"""

RETRY_STATUS_CODES = [
    408,  # Request timeout
    429,  # Too many requests
    502,  # Bad gateway
    503,  # Service unavailable
    504,  # Gateway timeout
]
"""Status codes which should trigger a retry attempt."""

RATE_LIMIT_HEADERS = ("X-RateLimit-Reset", "RateLimit-Reset", "X-Rate-Limit-Reset")
"""Common header names that indicate when a rate limited endpoint will reset."""

DEFAULT_JWT_OPTIONS = {"verify_signature": False, "verify_aud": False}
"""Default options for decoding JWT values."""
