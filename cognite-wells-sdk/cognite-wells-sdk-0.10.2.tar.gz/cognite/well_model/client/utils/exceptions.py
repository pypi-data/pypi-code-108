import json
from typing import Callable, Dict, List


class CogniteException(Exception):
    pass


class CogniteConnectionError(CogniteException):
    pass


class CogniteConnectionRefused(CogniteConnectionError):
    pass


class CogniteReadTimeout(CogniteException):
    pass


class CogniteAPIKeyError(CogniteException):
    """Cognite API Key Error.
    Raised if the API key is missing or invalid.
    """

    pass


class CogniteInvalidInput(CogniteException):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return f"Invalid input: {self.message}"


class CogniteMultiException(CogniteException):
    def __init__(self, successful: List = None, failed: List = None, unknown: List = None, unwrap_fn: Callable = None):
        self.successful = successful or []
        self.failed = failed or []
        self.unknown = unknown or []
        self._unwrap_fn = unwrap_fn or (lambda x: x)

    def _get_multi_exception_summary(self):
        if len(self.successful) > 0 or len(self.unknown) > 0 or len(self.failed) > 0:
            return (
                f"\nThe API Failed to process some items."
                f"\nSuccessful (2xx): {[self._unwrap_fn(f) for f in self.successful]}"
                f"\nUnknown (5xx): {[self._unwrap_fn(f) for f in self.unknown]}"
                f"\nFailed (4xx): {[self._unwrap_fn(f) for f in self.failed]}"
            )
        return ""


class CogniteAPIError(CogniteMultiException):
    def __init__(
        self,
        message: str,
        code: int = None,
        x_request_id: str = None,
        missing: List = None,
        duplicated: List = None,
        successful: List = None,
        failed: List = None,
        unknown: List = None,
        unwrap_fn: Callable = None,
        extra: Dict = None,
    ):
        self.message = message
        self.code = code
        self.x_request_id = x_request_id
        self.missing = missing
        self.duplicated = duplicated
        self.extra = extra
        super().__init__(successful, failed, unknown, unwrap_fn)

    def __str__(self):
        msg = f"{self.message} | code: {self.code} | X-request-Id: {self.x_request_id}"
        if self.missing:
            msg += f"\n Missing: {self.missing}"
        if self.duplicated:
            msg += f"\n Duplicated: {self.duplicated}"
        msg += self._get_multi_exception_summary()
        if self.extra:
            pretty_extra = json.dumps(self.extra, indent=4, sort_keys=True)
            msg += f"\n Additional error info: {pretty_extra}"
        return msg
