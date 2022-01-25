"""
Exceptions used in Taktile Client
"""


class TaktileClientException(Exception):
    """A generic taktile client exception"""


class HTTPException(TaktileClientException):
    """A Exception that is the result from an HTTP Exception"""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__()
        self._status_code = status_code
        self._detail = detail

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return (
            f"{class_name}"
            f"(status_code={self._status_code!r}, detail={self._detail!r})"
        )


class APIClientExceptionRetryable(HTTPException):
    """A retryable client api exception"""


class APIClientException(HTTPException):
    """A generic client api exception"""


class SerializationError(TaktileClientException):
    """A serialization exception"""


class IncompatibleVersionError(TaktileClientException):
    """Client server version is not compatible"""
