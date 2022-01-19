# High level events that make up HTTP/1.1 conversations. Loosely inspired by
# the corresponding events in hyper-h2:
#
#     http://python-hyper.org/h2/en/stable/api.html#events
#
# Don't subclass these. Stuff will break.

import re
from abc import ABC
from dataclasses import dataclass, field
from typing import Any, cast, Dict, List, Tuple, Union

from ._abnf import method, request_target
from ._headers import Headers, normalize_and_validate
from ._util import bytesify, LocalProtocolError, validate

# Everything in __all__ gets re-exported as part of the h11 public API.
__all__ = [
    "Event",
    "Request",
    "InformationalResponse",
    "Response",
    "Data",
    "EndOfMessage",
    "ConnectionClosed",
]

method_re = re.compile(method.encode("ascii"))
request_target_re = re.compile(request_target.encode("ascii"))


class Event(ABC):
    """
    Base class for h11 events.
    """

    __slots__ = ()


@dataclass(init=False, frozen=True)
class Request(Event):
    """The beginning of an HTTP request.

    Fields:

    .. attribute:: method

       An HTTP method, e.g. ``b"GET"`` or ``b"POST"``. Always a byte
       string. :term:`Bytes-like objects <bytes-like object>` and native
       strings containing only ascii characters will be automatically
       converted to byte strings.

    .. attribute:: target

       The target of an HTTP request, e.g. ``b"/index.html"``, or one of the
       more exotic formats described in `RFC 7320, section 5.3
       <https://tools.ietf.org/html/rfc7230#section-5.3>`_. Always a byte
       string. :term:`Bytes-like objects <bytes-like object>` and native
       strings containing only ascii characters will be automatically
       converted to byte strings.

    .. attribute:: headers

       Request headers, represented as a list of (name, value) pairs. See
       :ref:`the header normalization rules <headers-format>` for details.

    .. attribute:: http_version

       The HTTP protocol version, represented as a byte string like
       ``b"1.1"``. See :ref:`the HTTP version normalization rules
       <http_version-format>` for details.

    """

    __slots__ = ("method", "headers", "target", "http_version")

    method: bytes
    headers: Headers
    target: bytes
    http_version: bytes

    def __init__(
        self,
        *,
        method: Union[bytes, str],
        headers: Union[Headers, List[Tuple[bytes, bytes]], List[Tuple[str, str]]],
        target: Union[bytes, str],
        http_version: Union[bytes, str] = b"1.1",
        _parsed: bool = False,
    ) -> None:
        super().__init__()
        if isinstance(headers, Headers):
            object.__setattr__(self, "headers", headers)
        else:
            object.__setattr__(
                self, "headers", normalize_and_validate(headers, _parsed=_parsed)
            )
        if not _parsed:
            object.__setattr__(self, "method", bytesify(method))
            object.__setattr__(self, "target", bytesify(target))
            object.__setattr__(self, "http_version", bytesify(http_version))
        else:
            object.__setattr__(self, "method", method)
            object.__setattr__(self, "target", target)
            object.__setattr__(self, "http_version", http_version)

        # "A server MUST respond with a 400 (Bad Request) status code to any
        # HTTP/1.1 request message that lacks a Host header field and to any
        # request message that contains more than one Host header field or a
        # Host header field with an invalid field-value."
        # -- https://tools.ietf.org/html/rfc7230#section-5.4
        host_count = 0
        for name, value in self.headers:
            if name == b"host":
                host_count += 1
        if self.http_version == b"1.1" and host_count == 0:
            raise LocalProtocolError("Missing mandatory Host: header")
        if host_count > 1:
            raise LocalProtocolError("Found multiple Host: headers")

        validate(method_re, self.method, "Illegal method characters")
        validate(request_target_re, self.target, "Illegal target characters")

    # This is an unhashable type.
    __hash__ = None  # type: ignore


@dataclass(init=False, frozen=True)
class _ResponseBase(Event):
    __slots__ = ("headers", "http_version", "reason", "status_code")

    headers: Headers
    http_version: bytes
    reason: bytes
    status_code: int

    def __init__(
        self,
        *,
        headers: Union[Headers, List[Tuple[bytes, bytes]], List[Tuple[str, str]]],
        status_code: int,
        http_version: Union[bytes, str] = b"1.1",
        reason: Union[bytes, str] = b"",
        _parsed: bool = False,
    ) -> None:
        super().__init__()
        if isinstance(headers, Headers):
            object.__setattr__(self, "headers", headers)
        else:
            object.__setattr__(
                self, "headers", normalize_and_validate(headers, _parsed=_parsed)
            )
        if not _parsed:
            object.__setattr__(self, "reason", bytesify(reason))
            object.__setattr__(self, "http_version", bytesify(http_version))
            if not isinstance(status_code, int):
                raise LocalProtocolError("status code must be integer")
            # Because IntEnum objects are instances of int, but aren't
            # duck-compatible (sigh), see gh-72.
            object.__setattr__(self, "status_code", int(status_code))
        else:
            object.__setattr__(self, "reason", reason)
            object.__setattr__(self, "http_version", http_version)
            object.__setattr__(self, "status_code", status_code)

        self.__post_init__()

    def __post_init__(self) -> None:
        pass

    # This is an unhashable type.
    __hash__ = None  # type: ignore


@dataclass(init=False, frozen=True)
class InformationalResponse(_ResponseBase):
    """An HTTP informational response.

    Fields:

    .. attribute:: status_code

       The status code of this response, as an integer. For an
       :class:`InformationalResponse`, this is always in the range [100,
       200).

    .. attribute:: headers

       Request headers, represented as a list of (name, value) pairs. See
       :ref:`the header normalization rules <headers-format>` for
       details.

    .. attribute:: http_version

       The HTTP protocol version, represented as a byte string like
       ``b"1.1"``. See :ref:`the HTTP version normalization rules
       <http_version-format>` for details.

    .. attribute:: reason

       The reason phrase of this response, as a byte string. For example:
       ``b"OK"``, or ``b"Not Found"``.

    """

    def __post_init__(self) -> None:
        if not (100 <= self.status_code < 200):
            raise LocalProtocolError(
                "InformationalResponse status_code should be in range "
                "[100, 200), not {}".format(self.status_code)
            )

    # This is an unhashable type.
    __hash__ = None  # type: ignore


@dataclass(init=False, frozen=True)
class Response(_ResponseBase):
    """The beginning of an HTTP response.

    Fields:

    .. attribute:: status_code

       The status code of this response, as an integer. For an
       :class:`Response`, this is always in the range [200,
       1000).

    .. attribute:: headers

       Request headers, represented as a list of (name, value) pairs. See
       :ref:`the header normalization rules <headers-format>` for details.

    .. attribute:: http_version

       The HTTP protocol version, represented as a byte string like
       ``b"1.1"``. See :ref:`the HTTP version normalization rules
       <http_version-format>` for details.

    .. attribute:: reason

       The reason phrase of this response, as a byte string. For example:
       ``b"OK"``, or ``b"Not Found"``.

    """

    def __post_init__(self) -> None:
        if not (200 <= self.status_code < 1000):
            raise LocalProtocolError(
                "Response status_code should be in range [200, 1000), not {}".format(
                    self.status_code
                )
            )

    # This is an unhashable type.
    __hash__ = None  # type: ignore


@dataclass(init=False, frozen=True)
class Data(Event):
    """Part of an HTTP message body.

    Fields:

    .. attribute:: data

       A :term:`bytes-like object` containing part of a message body. Or, if
       using the ``combine=False`` argument to :meth:`Connection.send`, then
       any object that your socket writing code knows what to do with, and for
       which calling :func:`len` returns the number of bytes that will be
       written -- see :ref:`sendfile` for details.

    .. attribute:: chunk_start

       A marker that indicates whether this data object is from the start of a
       chunked transfer encoding chunk. This field is ignored when when a Data
       event is provided to :meth:`Connection.send`: it is only valid on
       events emitted from :meth:`Connection.next_event`. You probably
       shouldn't use this attribute at all; see
       :ref:`chunk-delimiters-are-bad` for details.

    .. attribute:: chunk_end

       A marker that indicates whether this data object is the last for a
       given chunked transfer encoding chunk. This field is ignored when when
       a Data event is provided to :meth:`Connection.send`: it is only valid
       on events emitted from :meth:`Connection.next_event`. You probably
       shouldn't use this attribute at all; see
       :ref:`chunk-delimiters-are-bad` for details.

    """

    __slots__ = ("data", "chunk_start", "chunk_end")

    data: bytes
    chunk_start: bool
    chunk_end: bool

    def __init__(
        self, data: bytes, chunk_start: bool = False, chunk_end: bool = False
    ) -> None:
        object.__setattr__(self, "data", data)
        object.__setattr__(self, "chunk_start", chunk_start)
        object.__setattr__(self, "chunk_end", chunk_end)

    # This is an unhashable type.
    __hash__ = None  # type: ignore


# XX FIXME: "A recipient MUST ignore (or consider as an error) any fields that
# are forbidden to be sent in a trailer, since processing them as if they were
# present in the header section might bypass external security filters."
# https://svn.tools.ietf.org/svn/wg/httpbis/specs/rfc7230.html#chunked.trailer.part
# Unfortunately, the list of forbidden fields is long and vague :-/
@dataclass(init=False, frozen=True)
class EndOfMessage(Event):
    """The end of an HTTP message.

    Fields:

    .. attribute:: headers

       Default value: ``[]``

       Any trailing headers attached to this message, represented as a list of
       (name, value) pairs. See :ref:`the header normalization rules
       <headers-format>` for details.

       Must be empty unless ``Transfer-Encoding: chunked`` is in use.

    """

    __slots__ = ("headers",)

    headers: Headers

    def __init__(
        self,
        *,
        headers: Union[
            Headers, List[Tuple[bytes, bytes]], List[Tuple[str, str]], None
        ] = None,
        _parsed: bool = False,
    ) -> None:
        super().__init__()
        if headers is None:
            headers = Headers([])
        elif not isinstance(headers, Headers):
            headers = normalize_and_validate(headers, _parsed=_parsed)

        object.__setattr__(self, "headers", headers)

    # This is an unhashable type.
    __hash__ = None  # type: ignore


@dataclass(frozen=True)
class ConnectionClosed(Event):
    """This event indicates that the sender has closed their outgoing
    connection.

    Note that this does not necessarily mean that they can't *receive* further
    data, because TCP connections are composed to two one-way channels which
    can be closed independently. See :ref:`closing` for details.

    No fields.
    """

    pass
