from .auth_adapter import JWTHeaderAuth, JobHeaderAuth, get_auth_instance
from .retry import RateLimitRetry
from .http_adapter import TimeoutHTTPAdapter
from .session import ExtendedSession
from .settings import POOL_CONNECTIONS, POOL_MAXSIZE, RETRIES, RETRY_STATUS_CODES, RETRY_BACKOFF
from .hooks import log_responses

# Setup a reasonable retry strategy
retry_strategy = RateLimitRetry(
    total=RETRIES,
    backoff_factor=RETRY_BACKOFF,
    status_forcelist=RETRY_STATUS_CODES,
    method_whitelist=["HEAD", "GET", "PUT", "POST", "PATCH", "DELETE", "TRACE"],
)

# Create a global DefaultHTTPAdapter to allow connection pooling for cases where concurrent requests are dispatched
adapter = TimeoutHTTPAdapter(
    pool_connections=POOL_CONNECTIONS,
    pool_maxsize=POOL_MAXSIZE,
    max_retries=retry_strategy,
)


def get_session() -> ExtendedSession:
    """Create a requests Session with a retry strategy and timeout set suitable for production use."""
    session = ExtendedSession()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.hooks["response"] = [log_responses]
    return session


__all__ = (
    "adapter",
    "ExtendedSession",
    "get_auth_instance",
    "get_session",
    "JobHeaderAuth",
    "JWTHeaderAuth",
    "RateLimitRetry",
    "retry_strategy",
    "TimeoutHTTPAdapter",
)
