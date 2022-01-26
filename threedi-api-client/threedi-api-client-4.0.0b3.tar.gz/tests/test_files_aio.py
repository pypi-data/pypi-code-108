import io
from concurrent.futures import ThreadPoolExecutor

import pytest
from aiofiles.threadpool import AsyncBufferedIOBase

# note: unittest.mock has no asyncio support in Python < 3.7,
# but luckily mock backported it:
from mock import AsyncMock, DEFAULT, Mock, patch

from threedi_api_client.openapi import ApiException
from threedi_api_client.aio.files import (
    download_file,
    download_fileobj,
    upload_file,
    upload_fileobj,
    DEFAULT_DOWNLOAD_TIMEOUT,
    DEFAULT_UPLOAD_TIMEOUT,
)


class AsyncBytesIO:
    """Just for testing, dumb async version of BytesIO"""

    def __init__(self):
        self._io = io.BytesIO()

    async def tell(self, *args, **kwargs):
        return self._io.tell(*args, **kwargs)

    async def seek(self, *args, **kwargs):
        return self._io.seek(*args, **kwargs)

    async def read(self, *args, **kwargs):
        return self._io.read(*args, **kwargs)

    async def write(self, *args, **kwargs):
        return self._io.write(*args, **kwargs)


@pytest.fixture
async def aio_request():
    with patch("aiohttp.ClientSession.request", new_callable=AsyncMock) as aio_request:
        yield aio_request


@pytest.fixture
async def response_error():
    # mimics aiohttp.ClientResponse
    response = AsyncMock()
    response.status = 503
    return response


@pytest.fixture
async def responses_single():
    # mimics aiohttp.ClientResponse
    response = AsyncMock()
    response.headers = {"Content-Range": "bytes 0-41/42"}
    response.status = 206
    response.read = AsyncMock(return_value=b"X" * 42)
    return [response]


@pytest.fixture
async def responses_double():
    # mimics aiohttp.ClientResponse
    response1 = AsyncMock()
    response1.headers = {"Content-Range": "bytes 0-63/65"}
    response1.status = 206
    response1.read = AsyncMock(return_value=b"X" * 64)
    response2 = AsyncMock()
    response2.headers = {"Content-Range": "bytes 64-64/65"}
    response2.status = 206
    response2.read = AsyncMock(return_value=b"X")
    return [response1, response2]


@pytest.mark.asyncio
async def test_download_fileobj(aio_request, responses_single):
    stream = AsyncBytesIO()
    aio_request.side_effect = responses_single

    await download_fileobj("some-url", stream, chunk_size=64)

    aio_request.assert_called_with(
        "GET",
        "some-url",
        headers={"Range": "bytes=0-63"},
        timeout=DEFAULT_DOWNLOAD_TIMEOUT,
    )
    assert await stream.tell() == 42


@pytest.mark.asyncio
async def test_download_fileobj_two_chunks(aio_request, responses_double):
    stream = AsyncBytesIO()
    aio_request.side_effect = responses_double

    callback_func = AsyncMock()

    await download_fileobj("some-url", stream, chunk_size=64, callback_func=callback_func)

    (_, kwargs1), (_, kwargs2) = aio_request.call_args_list
    assert kwargs1["headers"] == {"Range": "bytes=0-63"}
    assert kwargs2["headers"] == {"Range": "bytes=64-127"}
    assert await stream.tell() == 65

    # Check callback func
    (args1, _), (args2, _) = callback_func.call_args_list

    assert args1 == (63, 65)
    assert args2 == (65, 65)


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_download_fileobj_retry(
    sleep, aio_request, responses_double, response_error
):
    stream = AsyncBytesIO()
    responses = [
        response_error,
        responses_double[0],
        response_error,
        response_error,
        responses_double[1],
    ]
    aio_request.side_effect = responses

    await download_fileobj(
        "some-url", stream, chunk_size=64, retries=3, backoff_factor=1.5
    )

    assert aio_request.call_count == 5
    assert sleep.call_count == 3
    assert [x[0][0] for x in sleep.call_args_list] == [1.5, 1.5, 3.0]
    assert await stream.tell() == 65


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_download_fileobj_retry_limit(sleep, aio_request, response_error):
    aio_request.side_effect = [response_error] * 2

    with pytest.raises(ApiException) as e:
        await download_fileobj("some-url", None, chunk_size=64, retries=2)

    assert e.value.status == response_error.status
    assert aio_request.call_count == 2


@pytest.mark.asyncio
async def test_download_fileobj_no_multipart(aio_request, responses_single):
    """The remote server does not support range requests"""
    responses_single[0].status = 200
    aio_request.side_effect = responses_single

    with pytest.raises(ApiException) as e:
        await download_fileobj("some-url", None, chunk_size=64)

    assert e.value.status == 200
    assert e.value.reason == "The file server does not support multipart downloads."


@pytest.mark.asyncio
async def test_download_fileobj_forbidden_2nd_chunk(aio_request, responses_double):
    """The remote server does not support range requests"""
    stream = AsyncBytesIO()
    responses_double[1].status = 403
    aio_request.side_effect = responses_double

    with pytest.raises(ApiException) as e:
        await download_fileobj("some-url", stream, chunk_size=64)

    assert e.value.status == 403


@pytest.mark.asyncio
async def test_download_fileobj_forbidden(aio_request, response_error):
    """The remote server does not support range requests"""
    response_error.status = 403
    aio_request.side_effect = [response_error]

    with pytest.raises(ApiException) as e:
        await download_fileobj("some-url", None, chunk_size=64)

    assert e.value.status == 403


@pytest.mark.asyncio
@patch("threedi_api_client.aio.files.download_fileobj", new_callable=AsyncMock)
async def test_download_file(mocked_download_fileobj, tmp_path):
    executor = ThreadPoolExecutor()

    await download_file(
        "http://domain/a.b",
        tmp_path / "c.d",
        chunk_size=64,
        timeout=3.0,
        connector="foo",
        executor=executor,
        retries=2,
        backoff_factor=1.5,
    )

    args, kwargs = mocked_download_fileobj.call_args
    assert args[0] == "http://domain/a.b"
    assert isinstance(args[1], AsyncBufferedIOBase)
    assert args[1].mode == "wb"
    assert args[1].name == str(tmp_path / "c.d")
    assert kwargs["chunk_size"] == 64
    assert kwargs["timeout"] == 3.0
    assert kwargs["connector"] == "foo"
    assert kwargs["retries"] == 2
    assert kwargs["backoff_factor"] == 1.5
    assert "executor" not in kwargs  # download_fileobj does not expect it


@pytest.mark.asyncio
@patch("threedi_api_client.aio.files.download_fileobj", new_callable=AsyncMock)
async def test_download_file_directory(mocked_download_fileobj, tmp_path):
    # if a target directory is specified, a filename is created from the url
    await download_file(
        "http://domain/a.b", tmp_path, chunk_size=64, timeout=3.0, connector="foo"
    )

    args, kwargs = mocked_download_fileobj.call_args
    assert args[1].name == str(tmp_path / "a.b")


@pytest.fixture
async def upload_response():
    response = AsyncMock()
    response.status = 200
    return response


@pytest.fixture
async def fileobj():
    stream = AsyncBytesIO()
    await stream.write(b"X" * 39)
    await stream.seek(0)
    return stream


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "chunk_size,expected_body",
    [
        (64, [b"X" * 39]),
        (39, [b"X" * 39]),
        (38, [b"X" * 38, b"X"]),
        (16, [b"X" * 16, b"X" * 16, b"X" * 7]),
    ],
)
async def test_upload_fileobj(
    aio_request, fileobj, upload_response, chunk_size, expected_body
):
    aio_request.return_value = upload_response
    await upload_fileobj("some-url", fileobj, chunk_size=chunk_size)

    # base64.b64encode(hashlib.md5(b"X" * 39).digest()).decode()
    expected_md5 = "Q2zMNJgyazDIkoSqvpOqVg=="

    args, kwargs = aio_request.call_args
    assert args == ("PUT", "some-url")
    assert [x async for x in kwargs["data"]] == expected_body
    assert kwargs["headers"] == {"Content-Length": "39", "Content-MD5": expected_md5}
    assert kwargs["timeout"] == DEFAULT_UPLOAD_TIMEOUT


@pytest.mark.asyncio
async def test_upload_fileobj_callback(
    aio_request, fileobj, upload_response
):
    expected_body = [b"X" * 16, b"X" * 16, b"X" * 7]
    chunk_size = 16 

    callback_func = AsyncMock()

    aio_request.return_value = upload_response
    await upload_fileobj("some-url", fileobj, chunk_size=chunk_size, callback_func=callback_func)

    # base64.b64encode(hashlib.md5(b"X" * 39).digest()).decode()
    expected_md5 = "Q2zMNJgyazDIkoSqvpOqVg=="

    args, kwargs = aio_request.call_args
    assert args == ("PUT", "some-url")
    assert [x async for x in kwargs["data"]] == expected_body
    assert kwargs["headers"] == {"Content-Length": "39", "Content-MD5": expected_md5}
    assert kwargs["timeout"] == DEFAULT_UPLOAD_TIMEOUT

    # Check callback_func
    (args1, _), (args2, _), (args3, _) = callback_func.call_args_list
    assert args1 == (16, 39)
    assert args2 == (32, 39)
    assert args3 == (39, 39)


@pytest.mark.asyncio
async def test_upload_fileobj_with_md5(aio_request, fileobj, upload_response):
    aio_request.return_value = upload_response
    await upload_fileobj("some-url", fileobj, md5=b"abcd")

    # base64.b64encode(b"abcd")).decode()
    expected_md5 = "YWJjZA=="

    args, kwargs = aio_request.call_args
    assert kwargs["headers"] == {"Content-Length": "39", "Content-MD5": expected_md5}


@pytest.mark.asyncio
async def test_upload_fileobj_empty_file():
    with pytest.raises(IOError, match="The file object is empty."):
        await upload_fileobj("some-url", AsyncBytesIO())


@pytest.mark.asyncio
async def test_upload_fileobj_non_binary_file():
    string_io = AsyncMock()
    string_io.read = AsyncMock(return_value="some string")
    with pytest.raises(IOError, match="The file object is not in binary*"):
        await upload_fileobj("some-url", string_io)


@pytest.mark.asyncio
async def test_upload_fileobj_errors(aio_request, fileobj, upload_response):
    upload_response.status = 400
    aio_request.return_value = upload_response
    with pytest.raises(ApiException) as e:
        await upload_fileobj("some-url", fileobj)

    assert e.value.status == 400


@pytest.mark.asyncio
@patch("threedi_api_client.aio.files.upload_fileobj", new_callable=AsyncMock)
async def test_upload_file(upload_fileobj, tmp_path):
    executor = ThreadPoolExecutor()

    path = tmp_path / "myfile"
    with path.open("wb") as f:
        f.write(b"X")

    await upload_file(
        "http://domain/a.b",
        path,
        chunk_size=1234,
        timeout=3.0,
        connector="foo",
        executor=executor,
        md5=b"abcd",
        retries=2,
        backoff_factor=1.5,
    )

    args, kwargs = upload_fileobj.call_args
    assert args[0] == "http://domain/a.b"
    assert isinstance(args[1], AsyncBufferedIOBase)
    assert args[1].mode == "rb"
    assert args[1].name == str(path)
    assert kwargs["timeout"] == 3.0
    assert kwargs["chunk_size"] == 1234
    assert kwargs["md5"] == b"abcd"
    assert kwargs["connector"] == "foo"
    assert kwargs["executor"] is executor
    assert kwargs["retries"] == 2
    assert kwargs["backoff_factor"] == 1.5
