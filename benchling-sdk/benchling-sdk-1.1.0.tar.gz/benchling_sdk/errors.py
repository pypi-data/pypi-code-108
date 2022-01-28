from dataclasses import dataclass
import json
from json import JSONDecodeError
from typing import Any, Dict, MutableMapping, Optional, Union

from benchling_api_client.types import Response
from benchling_sdk.helpers.logging_helpers import default_logger
from benchling_sdk.helpers.serialization_helpers import unset_as_none
from benchling_sdk.models import (
    AsyncTask,
    AsyncTaskStatus,
    BadRequestError,
    BadRequestErrorBulk,
    ConflictError,
    ForbiddenError,
    NotFoundError,
)

logger = default_logger()


@dataclass
class BenchlingError(Exception):
    """An error resulting from communicating with the Benchling API.

    This could be an error returned from the API intentionally (e.g., 400 Bad Request) or an
    unexpected transport error (e.g., 502 Bad Gateway)

    The json attribute is present if the API response provided a deserializable JSON body as part of the
    error description. It will be None if the response could not be parsed as JSON.

    The content attribute is any unparsed content returned as part of the response body.
    """

    status_code: int
    headers: MutableMapping[str, str]
    json: Optional[Dict[str, str]]
    content: Optional[bytes]
    parsed: Union[
        None,
        ForbiddenError,
        NotFoundError,
        BadRequestError,
        BadRequestErrorBulk,
        ConflictError,
    ]

    @classmethod
    def from_response(cls, response: Response) -> "BenchlingError":
        """Create a BenchlingError from a generated Response."""
        json_body = _parse_error_body(response.content)
        return cls(
            status_code=response.status_code,
            headers=response.headers,
            json=json_body,
            content=response.content,
            parsed=response.parsed,
        )

    def __str__(self):
        message = self.json if self.json else self.content
        return f"{self.__class__.__name__}(status_code={self.status_code}, message={message})"


@dataclass
class RegistrationError(Exception):
    """An error relating to Benchling registration."""

    message: Optional[str] = None
    errors: Optional[Dict[Any, Any]] = None
    task_status: Optional[AsyncTaskStatus] = None

    @classmethod
    def from_task(cls, task: AsyncTask) -> "RegistrationError":
        """Create a RegistrationError from a failed AsyncTask."""
        task_errors = unset_as_none(task.errors)
        errors_dict: Dict[Any, Any] = task_errors.to_dict() if task_errors else dict()  # type: ignore
        return cls(message=unset_as_none(task.message), errors=errors_dict, task_status=task.status)

    def __str__(self):
        return repr(self)


@dataclass
class WaitForTaskExpiredError(Exception):
    """An error indicating an AsyncTask did not complete in the time allotted for polling."""

    message: str
    task: AsyncTask

    def __str__(self):
        return repr(self)


def raise_for_status(response: Response) -> None:
    """Evaluate a Response for a successful HTTP status code or raise a BenchlingError."""
    logger.info("Status: %s", response.status_code)
    logger.debug(response)
    if response.status_code < 200 or response.status_code >= 300:
        raise BenchlingError.from_response(response)


def _parse_error_body(content: bytes) -> Optional[Dict[str, str]]:
    if content:
        string_content = content.decode("utf-8")
        # In case the response is not a serialized JSON dict (e.g. a gateway error)
        try:
            return json.loads(string_content)
        except JSONDecodeError:
            # Some responses may not be JSON. Just catch the error
            return None
    return None
