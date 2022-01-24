from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Generic, Literal, Optional, TypeVar, overload

from pydantic import Extra, Field
from pydantic.generics import GenericModel

from .io import dump
from .requests import Request


T = TypeVar("T")
DefaultMsgT = bytes


class Response(GenericModel, Generic[T]):
    """A class used to store subscription response data"""

    success: bool
    details: Optional[str] = None
    code: int
    error: Optional[str] = None
    data: Optional[T] = None
    exception: Optional[Exception] = None
    content_type: Optional[str] = Field(None, alias="content-type")
    content_encoding: Optional[str] = Field(None, alias="content-encoding")
    process_duration: Optional[float] = Field(None, alias="x-process-duration")
    publish_time: Optional[datetime] = Field(None, alias="x-publish-time")
    request_origin: Optional[str] = Field(None, alias="x-request-origin")
    request_duration: Optional[float] = Field(None, alias="x-request-duration")
    request_timeout: Optional[float] = Field(None, alias="x-request-timeout")
    process_timeout: Optional[float] = Field(None, alias="x-process-timeout")
    # FIXME: This is a bit ugly, but really useful for tests
    abort: Optional[bool] = Field(None, alias="x-abort-response")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        extra = Extra.allow

    def _format_header_value(self, key: str, value: Any, line_sep: str = " - ") -> str:
        # Make sure values never contain "\n" (line break is not valid is NATS headers)
        # User can configure which line separator use
        return line_sep.join(value.strip() for value in str(value).split("\n"))

    def get_headers(self, line_sep: str = " - ") -> Dict[str, str]:
        """Get all response headers"""
        hdrs = {
            key: self._format_header_value(key, value, line_sep)
            for key, value in self.dict(
                exclude={"data", "exception"},
                exclude_unset=True,
                exclude_none=True,
                by_alias=True,
            ).items()
        }
        # Make sure all boolean header values are in lower case
        hdrs["success"] = hdrs["success"].lower()

        return hdrs

    def get_data(self) -> Optional[T]:
        """Get response data"""
        return self.data

    def set_header(self, key: str, value: str) -> None:
        """Set a response header"""
        if key in ("exception", "data"):
            raise ValueError("'exception' and 'data' header names are not allowed")
        setattr(self, key, value)

    @overload
    def get_header(self, key: str, *, line_sep: str = " - ") -> str:
        ...  # pragma: no cover

    @overload
    def get_header(self, key: str, default: str, *, line_sep: str = " - ") -> str:
        ...  # pragma: no cover

    def get_header(self, key: str, default: str = ..., *, line_sep: str = " - ") -> str:  # type: ignore[assignment]
        """Get a response header"""
        if default is not ...:
            value = getattr(self, key, default)

        else:
            value = getattr(self, key)

        return self._format_header_value(key, value, line_sep=line_sep)

    def to_request(
        self,
        _type: Literal["publish", "subscribe", "reply", "request"],
        subject: str,
        reply: Optional[str] = None,
    ) -> Request:
        return Request(
            {
                "type": _type,
                "subject": subject,
                "reply": reply,
                "headers": self.get_headers(),
                "data": dump(self.data),
            }
        )


class Failure(Response[T]):
    """A class used to store failed subscription response"""

    success: Literal[False] = False


class Success(Response[T]):
    """A class used to store successful subscription response"""

    success: Literal[True] = True


__all__ = ["Response", "Failure", "Success"]
