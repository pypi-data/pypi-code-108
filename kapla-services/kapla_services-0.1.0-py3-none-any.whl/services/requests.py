from __future__ import annotations

from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Type,
    TypeVar,
    overload,
)

from .headers import Headers, HeaderTypes
from .io import dump
from .validation import validate

if TYPE_CHECKING:  # pragma: no cover
    from .broker import Broker  # pragma: no cover


class Subject(str):
    """A subject is simply a string."""

    @property
    def tokens(self) -> List[str]:
        """Retrieve all tokens from subject as a list of strings.

        An NATS token can be seen as one or several tokens separated by "." character.
        """
        return self.split(".")

    @property
    def last_token(self) -> str:
        """Retrieve last token from a subject as a string."""
        return self.tokens[-1]


class Reply(Subject):
    """A reply is simply a string."""


class State:
    """
    An object that can be used to store arbitrary state.
    Used for `request.state` and `app.state`.
    """

    def __init__(self, state: Optional[Dict[Any, Any]] = None):
        if state is None:
            state = {}
        super().__setattr__("_state", state)

    def __setattr__(self, key: Any, value: Any) -> None:
        self._state[key] = value

    def __getattr__(self, key: Any) -> Any:
        try:
            return self._state[key]
        except KeyError:
            message = "'{}' object has no attribute '{}'"
            raise AttributeError(message.format(self.__class__.__name__, key))

    def __delattr__(self, key: Any) -> None:
        del self._state[key]


class Request(Mapping[str, Any]):
    """A base class for publish and request operations"""

    def __init__(
        self,
        scope: MutableMapping[str, Any],
    ) -> None:
        assert scope["type"] in ("publish", "request", "reply", "subscribe")
        self.scope = scope
        self.scope["subject"] = Subject(self.scope["subject"])
        self.scope["reply"] = Reply(self.scope.get("reply", ""))
        self.scope["data"] = self.scope.get("data", b"")
        self.scope["headers"] = self.scope.get("headers", Headers()) or Headers()
        self.scope["state"] = State(self.scope.get("state", {}))

    def __getitem__(self, key: str) -> Any:
        return self.scope[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.scope)

    def __len__(self) -> int:
        return len(self.scope)

    @property
    def data(self) -> bytes:
        return self.scope["data"]  # type: ignore[no-any-return]

    @property
    def subject(self) -> Subject:
        return self.scope["subject"]  # type: ignore[no-any-return]

    @property
    def reply(self) -> Reply:
        return self.scope["reply"]  # type: ignore[no-any-return]

    @property
    def request_timeout(self) -> Optional[float]:
        """Get the request timeout as a float value"""
        if not hasattr(self, "_request_timeout"):
            if "x-request-timeout" not in self.headers:
                self._request_timeout = None
            else:
                self._request_timeout = self.headers["x-request-timeout"]
        return float(self._request_timeout) if self._request_timeout else None

    @property
    def process_timeout(self) -> Optional[float]:
        """Get the process timeout as a float value"""
        if not hasattr(self, "_process_timeout"):
            if "x-process-timeout" not in self.headers:
                self._process_timeout = None
            else:
                self._process_timeout = self.headers["x-process-timeout"]
        return (
            float(self._process_timeout)
            if self._process_timeout
            else self.request_timeout
        )

    @property
    def publish_time(self) -> Optional[datetime]:
        if not hasattr(self, "_publish_time"):
            if value := self.headers.get("x-publish-time", None):
                self._publish_time: Optional[datetime] = datetime.fromisoformat(value)
            else:
                self._publish_time = None
        return self._publish_time

    @property
    def content_type(self) -> Optional[str]:
        return self.headers.get("content-type", None)

    @property
    def content_encoding(self) -> Optional[str]:
        return self.headers.get("content-encoding", None)

    @property
    def headers(self) -> Headers:
        return self.scope["headers"]  # type: ignore[no-any-return]

    @property
    def broker(self) -> Broker:
        if not hasattr(self, "_broker"):
            self._broker = self.scope["broker"]
        return self._broker  # type: ignore[no-any-return]

    @property
    def state(self) -> State:
        return self.scope["state"]  # type: ignore[no-any-return]

    @classmethod
    def _from_publish(
        cls,
        subject: str,
        payload: Any = b"",
        reply: str = "",
        headers: Optional[HeaderTypes] = None,
        process_timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> Request:
        request = cls(
            {
                "type": "publish",
                "subject": subject,
                "reply": reply or Reply(""),
                "data": dump(payload, **kwargs),
                "headers": headers,
            }
        )
        if process_timeout:
            request.headers["x-process-timeout"] = f"{process_timeout:.3f}"
        return request

    @classmethod
    def _from_request(
        cls,
        subject: str,
        payload: Any = b"",
        headers: Optional[HeaderTypes] = None,
        timeout: float = 1.0,
        process_timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> Request:
        request = cls(
            {
                "type": "request",
                "subject": subject,
                "data": dump(payload, **kwargs),
                "headers": headers,
            }
        )
        # Consider timeout argument as request timeout
        request_timeout = timeout
        # Make sure a process_timeout exists
        process_timeout = process_timeout or timeout
        # # Make sure request_timeout is greater than process_timeout
        # if request_timeout < process_timeout:
        #     raise ValueError(
        #         f"Request timeout cannot be lower than process timeout (received request_timeout={request_timeout} < process_timeout={process_timeout} )."
        #     )
        # Add the timeout headers
        # Maximum precision is milliseconds
        request.headers["x-process-timeout"] = f"{process_timeout:.3f}"
        request.headers["x-request-timeout"] = f"{request_timeout:.3f}"
        # Return the request instance
        return request

    @classmethod
    def _from_subscribe(
        cls,
        subject: str,
        payload: bytes = b"",
        reply: str = "",
        headers: Optional[HeaderTypes] = None,
        **kwargs: Any,
    ) -> Request:
        return cls(
            {
                "type": "subscribe",
                "subject": subject,
                "data": payload,
                "reply": reply,
                "headers": headers,
            }
        )

    @classmethod
    def _from_reply(
        cls,
        subject: str,
        payload: bytes = b"",
        headers: Optional[HeaderTypes] = None,
        **kwargs: Any,
    ) -> Request:
        return cls(
            {
                "type": "reply",
                "subject": subject,
                "data": dump(payload, **kwargs),
                "headers": headers,
            }
        )


CastT = TypeVar("CastT")


class Header:
    """A class used to inject a single header value"""

    def __init__(self, key: str, default: Optional[str] = None) -> None:
        self.key = key
        self.default = default

    @overload
    def get(self, request: Request) -> str:
        ...  # pragma: no cover

    @overload
    def get(self, request: Request, _type: Type[CastT]) -> Optional[CastT]:
        ...  # pragma: no cover

    def get(self, request: Request, _type: Optional[Type[Any]] = None) -> Any:
        """By default header value is parsed as string
        but it can also be parsed into given type
        """
        value = request.headers.get(self.key, self.default)
        if _type:
            return validate(_type, value)
        return value


__all__ = [
    "Subject",
    "Reply",
    "Headers",
    "Header",
    "Request",
    "State",
]
