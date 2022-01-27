"""Declares standard exceptions."""
import json
import math

from unimatrix.ext.model import CanonicalException


class RateLimited(CanonicalException):
    """Raised when a request is rate limited."""
    http_status_code: int = 429
    code: str = 'RATELIMITED'

    def __init__(self, expires, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expires = expires

    def as_dict(self, *args, **kwargs) -> dict:
        return {
            **super().as_dict(*args, **kwargs),
            'spec': {
                'expires': self.expires
            }
        }


class Backoff(CanonicalException):
    """Raised when a backoff is enforced to a request"""
    http_status_code = 429
    code = 'BACKOFF'

    @staticmethod
    def add_to_exception(
        exception: Exception,
        ttl: int,
        expires: int,
        attempts: int,
        timestamp: int
    ) -> None:
        """Sets the backoff to an existing :class:`Exception`
        instance, if it is supported.
        """
        if isinstance(exception, CanonicalException):
            exception.set_backoff(ttl, expires, attempts, timestamp)

    @classmethod
    def fromserialized(cls, buf):
        """Instantiate a serialized :class:`Backoff` exception."""
        dto = json.loads(buf)
        return cls(
            seconds=math.ceil((dto['expires'] - dto['timestamp']) / 1000),
            attempts=0,
            **dto
        )

    def __init__(self,
        seconds: int,
        expires: int,
        attempts: int,
        timestamp: int
    ):
        """Initialize a new :class:`Backoff` instance."""
        self.seconds = seconds
        self.expires = expires
        self.attempts = attempts
        super().__init__(
            message="Requests to this resource are being rate limited.",
            hint="Respect the Retry-After header.",
        )
        self.set_backoff(seconds, expires, attempts, timestamp)

    def as_dict(self, *args, **kwargs) -> dict:
        return {
            **super().as_dict(*args, **kwargs),
            'spec': {
                'expires': self.expires,
                'seconds': self.seconds,
                'attempts': self.attempts
            }
        }

    def get_http_headers(self) -> dict:
        return {
            **super().get_http_headers(),
            'Retry-After': str(self.seconds)
        }
