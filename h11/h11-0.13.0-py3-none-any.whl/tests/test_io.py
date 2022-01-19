from typing import Any, Callable, Generator, List

import pytest

from .._events import (
    ConnectionClosed,
    Data,
    EndOfMessage,
    Event,
    InformationalResponse,
    Request,
    Response,
)
from .._headers import Headers, normalize_and_validate
from .._readers import (
    _obsolete_line_fold,
    ChunkedReader,
    ContentLengthReader,
    Http10Reader,
    READERS,
)
from .._receivebuffer import ReceiveBuffer
from .._state import (
    CLIENT,
    CLOSED,
    DONE,
    IDLE,
    MIGHT_SWITCH_PROTOCOL,
    MUST_CLOSE,
    SEND_BODY,
    SEND_RESPONSE,
    SERVER,
    SWITCHED_PROTOCOL,
)
from .._util import LocalProtocolError
from .._writers import (
    ChunkedWriter,
    ContentLengthWriter,
    Http10Writer,
    write_any_response,
    write_headers,
    write_request,
    WRITERS,
)
from .helpers import normalize_data_events

SIMPLE_CASES = [
    (
        (CLIENT, IDLE),
        Request(
            method="GET",
            target="/a",
            headers=[("Host", "foo"), ("Connection", "close")],
        ),
        b"GET /a HTTP/1.1\r\nHost: foo\r\nConnection: close\r\n\r\n",
    ),
    (
        (SERVER, SEND_RESPONSE),
        Response(status_code=200, headers=[("Connection", "close")], reason=b"OK"),
        b"HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n",
    ),
    (
        (SERVER, SEND_RESPONSE),
        Response(status_code=200, headers=[], reason=b"OK"),  # type: ignore[arg-type]
        b"HTTP/1.1 200 OK\r\n\r\n",
    ),
    (
        (SERVER, SEND_RESPONSE),
        InformationalResponse(
            status_code=101, headers=[("Upgrade", "websocket")], reason=b"Upgrade"
        ),
        b"HTTP/1.1 101 Upgrade\r\nUpgrade: websocket\r\n\r\n",
    ),
    (
        (SERVER, SEND_RESPONSE),
        InformationalResponse(status_code=101, headers=[], reason=b"Upgrade"),  # type: ignore[arg-type]
        b"HTTP/1.1 101 Upgrade\r\n\r\n",
    ),
]


def dowrite(writer: Callable[..., None], obj: Any) -> bytes:
    got_list: List[bytes] = []
    writer(obj, got_list.append)
    return b"".join(got_list)


def tw(writer: Any, obj: Any, expected: Any) -> None:
    got = dowrite(writer, obj)
    assert got == expected


def makebuf(data: bytes) -> ReceiveBuffer:
    buf = ReceiveBuffer()
    buf += data
    return buf


def tr(reader: Any, data: bytes, expected: Any) -> None:
    def check(got: Any) -> None:
        assert got == expected
        # Headers should always be returned as bytes, not e.g. bytearray
        # https://github.com/python-hyper/wsproto/pull/54#issuecomment-377709478
        for name, value in getattr(got, "headers", []):
            assert type(name) is bytes
            assert type(value) is bytes

    # Simple: consume whole thing
    buf = makebuf(data)
    check(reader(buf))
    assert not buf

    # Incrementally growing buffer
    buf = ReceiveBuffer()
    for i in range(len(data)):
        assert reader(buf) is None
        buf += data[i : i + 1]
    check(reader(buf))

    # Trailing data
    buf = makebuf(data)
    buf += b"trailing"
    check(reader(buf))
    assert bytes(buf) == b"trailing"


def test_writers_simple() -> None:
    for ((role, state), event, binary) in SIMPLE_CASES:
        tw(WRITERS[role, state], event, binary)


def test_readers_simple() -> None:
    for ((role, state), event, binary) in SIMPLE_CASES:
        tr(READERS[role, state], binary, event)


def test_writers_unusual() -> None:
    # Simple test of the write_headers utility routine
    tw(
        write_headers,
        normalize_and_validate([("foo", "bar"), ("baz", "quux")]),
        b"foo: bar\r\nbaz: quux\r\n\r\n",
    )
    tw(write_headers, Headers([]), b"\r\n")

    # We understand HTTP/1.0, but we don't speak it
    with pytest.raises(LocalProtocolError):
        tw(
            write_request,
            Request(
                method="GET",
                target="/",
                headers=[("Host", "foo"), ("Connection", "close")],
                http_version="1.0",
            ),
            None,
        )
    with pytest.raises(LocalProtocolError):
        tw(
            write_any_response,
            Response(
                status_code=200, headers=[("Connection", "close")], http_version="1.0"
            ),
            None,
        )


def test_readers_unusual() -> None:
    # Reading HTTP/1.0
    tr(
        READERS[CLIENT, IDLE],
        b"HEAD /foo HTTP/1.0\r\nSome: header\r\n\r\n",
        Request(
            method="HEAD",
            target="/foo",
            headers=[("Some", "header")],
            http_version="1.0",
        ),
    )

    # check no-headers, since it's only legal with HTTP/1.0
    tr(
        READERS[CLIENT, IDLE],
        b"HEAD /foo HTTP/1.0\r\n\r\n",
        Request(method="HEAD", target="/foo", headers=[], http_version="1.0"),  # type: ignore[arg-type]
    )

    tr(
        READERS[SERVER, SEND_RESPONSE],
        b"HTTP/1.0 200 OK\r\nSome: header\r\n\r\n",
        Response(
            status_code=200,
            headers=[("Some", "header")],
            http_version="1.0",
            reason=b"OK",
        ),
    )

    # single-character header values (actually disallowed by the ABNF in RFC
    # 7230 -- this is a bug in the standard that we originally copied...)
    tr(
        READERS[SERVER, SEND_RESPONSE],
        b"HTTP/1.0 200 OK\r\n" b"Foo: a a a a a \r\n\r\n",
        Response(
            status_code=200,
            headers=[("Foo", "a a a a a")],
            http_version="1.0",
            reason=b"OK",
        ),
    )

    # Empty headers -- also legal
    tr(
        READERS[SERVER, SEND_RESPONSE],
        b"HTTP/1.0 200 OK\r\n" b"Foo:\r\n\r\n",
        Response(
            status_code=200, headers=[("Foo", "")], http_version="1.0", reason=b"OK"
        ),
    )

    tr(
        READERS[SERVER, SEND_RESPONSE],
        b"HTTP/1.0 200 OK\r\n" b"Foo: \t \t \r\n\r\n",
        Response(
            status_code=200, headers=[("Foo", "")], http_version="1.0", reason=b"OK"
        ),
    )

    # Tolerate broken servers that leave off the response code
    tr(
        READERS[SERVER, SEND_RESPONSE],
        b"HTTP/1.0 200\r\n" b"Foo: bar\r\n\r\n",
        Response(
            status_code=200, headers=[("Foo", "bar")], http_version="1.0", reason=b""
        ),
    )

    # Tolerate headers line endings (\r\n and \n)
    #    \n\r\b between headers and body
    tr(
        READERS[SERVER, SEND_RESPONSE],
        b"HTTP/1.1 200 OK\r\nSomeHeader: val\n\r\n",
        Response(
            status_code=200,
            headers=[("SomeHeader", "val")],
            http_version="1.1",
            reason="OK",
        ),
    )

    #   delimited only with \n
    tr(
        READERS[SERVER, SEND_RESPONSE],
        b"HTTP/1.1 200 OK\nSomeHeader1: val1\nSomeHeader2: val2\n\n",
        Response(
            status_code=200,
            headers=[("SomeHeader1", "val1"), ("SomeHeader2", "val2")],
            http_version="1.1",
            reason="OK",
        ),
    )

    #   mixed \r\n and \n
    tr(
        READERS[SERVER, SEND_RESPONSE],
        b"HTTP/1.1 200 OK\r\nSomeHeader1: val1\nSomeHeader2: val2\n\r\n",
        Response(
            status_code=200,
            headers=[("SomeHeader1", "val1"), ("SomeHeader2", "val2")],
            http_version="1.1",
            reason="OK",
        ),
    )

    # obsolete line folding
    tr(
        READERS[CLIENT, IDLE],
        b"HEAD /foo HTTP/1.1\r\n"
        b"Host: example.com\r\n"
        b"Some: multi-line\r\n"
        b" header\r\n"
        b"\tnonsense\r\n"
        b"    \t   \t\tI guess\r\n"
        b"Connection: close\r\n"
        b"More-nonsense: in the\r\n"
        b"    last header  \r\n\r\n",
        Request(
            method="HEAD",
            target="/foo",
            headers=[
                ("Host", "example.com"),
                ("Some", "multi-line header nonsense I guess"),
                ("Connection", "close"),
                ("More-nonsense", "in the last header"),
            ],
        ),
    )

    with pytest.raises(LocalProtocolError):
        tr(
            READERS[CLIENT, IDLE],
            b"HEAD /foo HTTP/1.1\r\n" b"  folded: line\r\n\r\n",
            None,
        )

    with pytest.raises(LocalProtocolError):
        tr(
            READERS[CLIENT, IDLE],
            b"HEAD /foo HTTP/1.1\r\n" b"foo  : line\r\n\r\n",
            None,
        )
    with pytest.raises(LocalProtocolError):
        tr(
            READERS[CLIENT, IDLE],
            b"HEAD /foo HTTP/1.1\r\n" b"foo\t: line\r\n\r\n",
            None,
        )
    with pytest.raises(LocalProtocolError):
        tr(
            READERS[CLIENT, IDLE],
            b"HEAD /foo HTTP/1.1\r\n" b"foo\t: line\r\n\r\n",
            None,
        )
    with pytest.raises(LocalProtocolError):
        tr(READERS[CLIENT, IDLE], b"HEAD /foo HTTP/1.1\r\n" b": line\r\n\r\n", None)


def test__obsolete_line_fold_bytes() -> None:
    # _obsolete_line_fold has a defensive cast to bytearray, which is
    # necessary to protect against O(n^2) behavior in case anyone ever passes
    # in regular bytestrings... but right now we never pass in regular
    # bytestrings. so this test just exists to get some coverage on that
    # defensive cast.
    assert list(_obsolete_line_fold([b"aaa", b"bbb", b"  ccc", b"ddd"])) == [
        b"aaa",
        bytearray(b"bbb ccc"),
        b"ddd",
    ]


def _run_reader_iter(
    reader: Any, buf: bytes, do_eof: bool
) -> Generator[Any, None, None]:
    while True:
        event = reader(buf)
        if event is None:
            break
        yield event
        # body readers have undefined behavior after returning EndOfMessage,
        # because this changes the state so they don't get called again
        if type(event) is EndOfMessage:
            break
    if do_eof:
        assert not buf
        yield reader.read_eof()


def _run_reader(*args: Any) -> List[Event]:
    events = list(_run_reader_iter(*args))
    return normalize_data_events(events)


def t_body_reader(thunk: Any, data: bytes, expected: Any, do_eof: bool = False) -> None:
    # Simple: consume whole thing
    print("Test 1")
    buf = makebuf(data)
    assert _run_reader(thunk(), buf, do_eof) == expected

    # Incrementally growing buffer
    print("Test 2")
    reader = thunk()
    buf = ReceiveBuffer()
    events = []
    for i in range(len(data)):
        events += _run_reader(reader, buf, False)
        buf += data[i : i + 1]
    events += _run_reader(reader, buf, do_eof)
    assert normalize_data_events(events) == expected

    is_complete = any(type(event) is EndOfMessage for event in expected)
    if is_complete and not do_eof:
        buf = makebuf(data + b"trailing")
        assert _run_reader(thunk(), buf, False) == expected


def test_ContentLengthReader() -> None:
    t_body_reader(lambda: ContentLengthReader(0), b"", [EndOfMessage()])

    t_body_reader(
        lambda: ContentLengthReader(10),
        b"0123456789",
        [Data(data=b"0123456789"), EndOfMessage()],
    )


def test_Http10Reader() -> None:
    t_body_reader(Http10Reader, b"", [EndOfMessage()], do_eof=True)
    t_body_reader(Http10Reader, b"asdf", [Data(data=b"asdf")], do_eof=False)
    t_body_reader(
        Http10Reader, b"asdf", [Data(data=b"asdf"), EndOfMessage()], do_eof=True
    )


def test_ChunkedReader() -> None:
    t_body_reader(ChunkedReader, b"0\r\n\r\n", [EndOfMessage()])

    t_body_reader(
        ChunkedReader,
        b"0\r\nSome: header\r\n\r\n",
        [EndOfMessage(headers=[("Some", "header")])],
    )

    t_body_reader(
        ChunkedReader,
        b"5\r\n01234\r\n"
        + b"10\r\n0123456789abcdef\r\n"
        + b"0\r\n"
        + b"Some: header\r\n\r\n",
        [
            Data(data=b"012340123456789abcdef"),
            EndOfMessage(headers=[("Some", "header")]),
        ],
    )

    t_body_reader(
        ChunkedReader,
        b"5\r\n01234\r\n" + b"10\r\n0123456789abcdef\r\n" + b"0\r\n\r\n",
        [Data(data=b"012340123456789abcdef"), EndOfMessage()],
    )

    # handles upper and lowercase hex
    t_body_reader(
        ChunkedReader,
        b"aA\r\n" + b"x" * 0xAA + b"\r\n" + b"0\r\n\r\n",
        [Data(data=b"x" * 0xAA), EndOfMessage()],
    )

    # refuses arbitrarily long chunk integers
    with pytest.raises(LocalProtocolError):
        # Technically this is legal HTTP/1.1, but we refuse to process chunk
        # sizes that don't fit into 20 characters of hex
        t_body_reader(ChunkedReader, b"9" * 100 + b"\r\nxxx", [Data(data=b"xxx")])

    # refuses garbage in the chunk count
    with pytest.raises(LocalProtocolError):
        t_body_reader(ChunkedReader, b"10\x00\r\nxxx", None)

    # handles (and discards) "chunk extensions" omg wtf
    t_body_reader(
        ChunkedReader,
        b"5; hello=there\r\n"
        + b"xxxxx"
        + b"\r\n"
        + b'0; random="junk"; some=more; canbe=lonnnnngg\r\n\r\n',
        [Data(data=b"xxxxx"), EndOfMessage()],
    )


def test_ContentLengthWriter() -> None:
    w = ContentLengthWriter(5)
    assert dowrite(w, Data(data=b"123")) == b"123"
    assert dowrite(w, Data(data=b"45")) == b"45"
    assert dowrite(w, EndOfMessage()) == b""

    w = ContentLengthWriter(5)
    with pytest.raises(LocalProtocolError):
        dowrite(w, Data(data=b"123456"))

    w = ContentLengthWriter(5)
    dowrite(w, Data(data=b"123"))
    with pytest.raises(LocalProtocolError):
        dowrite(w, Data(data=b"456"))

    w = ContentLengthWriter(5)
    dowrite(w, Data(data=b"123"))
    with pytest.raises(LocalProtocolError):
        dowrite(w, EndOfMessage())

    w = ContentLengthWriter(5)
    dowrite(w, Data(data=b"123")) == b"123"
    dowrite(w, Data(data=b"45")) == b"45"
    with pytest.raises(LocalProtocolError):
        dowrite(w, EndOfMessage(headers=[("Etag", "asdf")]))


def test_ChunkedWriter() -> None:
    w = ChunkedWriter()
    assert dowrite(w, Data(data=b"aaa")) == b"3\r\naaa\r\n"
    assert dowrite(w, Data(data=b"a" * 20)) == b"14\r\n" + b"a" * 20 + b"\r\n"

    assert dowrite(w, Data(data=b"")) == b""

    assert dowrite(w, EndOfMessage()) == b"0\r\n\r\n"

    assert (
        dowrite(w, EndOfMessage(headers=[("Etag", "asdf"), ("a", "b")]))
        == b"0\r\nEtag: asdf\r\na: b\r\n\r\n"
    )


def test_Http10Writer() -> None:
    w = Http10Writer()
    assert dowrite(w, Data(data=b"1234")) == b"1234"
    assert dowrite(w, EndOfMessage()) == b""

    with pytest.raises(LocalProtocolError):
        dowrite(w, EndOfMessage(headers=[("Etag", "asdf")]))


def test_reject_garbage_after_request_line() -> None:
    with pytest.raises(LocalProtocolError):
        tr(READERS[SERVER, SEND_RESPONSE], b"HTTP/1.0 200 OK\x00xxxx\r\n\r\n", None)


def test_reject_garbage_after_response_line() -> None:
    with pytest.raises(LocalProtocolError):
        tr(
            READERS[CLIENT, IDLE],
            b"HEAD /foo HTTP/1.1 xxxxxx\r\n" b"Host: a\r\n\r\n",
            None,
        )


def test_reject_garbage_in_header_line() -> None:
    with pytest.raises(LocalProtocolError):
        tr(
            READERS[CLIENT, IDLE],
            b"HEAD /foo HTTP/1.1\r\n" b"Host: foo\x00bar\r\n\r\n",
            None,
        )


def test_reject_non_vchar_in_path() -> None:
    for bad_char in b"\x00\x20\x7f\xee":
        message = bytearray(b"HEAD /")
        message.append(bad_char)
        message.extend(b" HTTP/1.1\r\nHost: foobar\r\n\r\n")
        with pytest.raises(LocalProtocolError):
            tr(READERS[CLIENT, IDLE], message, None)


# https://github.com/python-hyper/h11/issues/57
def test_allow_some_garbage_in_cookies() -> None:
    tr(
        READERS[CLIENT, IDLE],
        b"HEAD /foo HTTP/1.1\r\n"
        b"Host: foo\r\n"
        b"Set-Cookie: ___utmvafIumyLc=kUd\x01UpAt; path=/; Max-Age=900\r\n"
        b"\r\n",
        Request(
            method="HEAD",
            target="/foo",
            headers=[
                ("Host", "foo"),
                ("Set-Cookie", "___utmvafIumyLc=kUd\x01UpAt; path=/; Max-Age=900"),
            ],
        ),
    )


def test_host_comes_first() -> None:
    tw(
        write_headers,
        normalize_and_validate([("foo", "bar"), ("Host", "example.com")]),
        b"Host: example.com\r\nfoo: bar\r\n\r\n",
    )
