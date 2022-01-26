import asyncio
import base64
import hashlib
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import Optional, Tuple, Union, Callable, Awaitable
from urllib.parse import urlparse

import aiofiles
import aiofiles.os
import aiohttp

from threedi_api_client.openapi import ApiException

CONTENT_RANGE_REGEXP = re.compile(r"^bytes (\d+)-(\d+)/(\d+|\*)$")
RETRY_STATUSES = frozenset({413, 429, 503})  # like in urllib3
DEFAULT_CONN_LIMIT = 4  # for downloads only (which are parrallel)
# only timeout on the socket, not on Python code (like urllib3)
DEFAULT_DOWNLOAD_TIMEOUT = aiohttp.ClientTimeout(
    total=None, sock_connect=5.0, sock_read=5.0
)
# Default upload timeout has an increased socket read timeout, because MinIO
# takes very long for completing the upload for larger files. The limit of 10 minutes
# should accomodate files up to 150 GB.
DEFAULT_UPLOAD_TIMEOUT = aiohttp.ClientTimeout(
    total=None, sock_connect=5.0, sock_read=600.0
)

logger = logging.getLogger(__name__)


async def _request_with_retry(request_coroutine, retries, backoff_factor):
    """Call a request coroutine and retry on ClientError or on 413/429/503.

    The default retry policy has 3 retries with 1, 2, 4 second intervals.
    """
    assert retries > 0
    for attempt in range(retries):
        if attempt > 0:
            backoff = backoff_factor * 2 ** (attempt - 1)
            logger.warning(
                "Retry attempt {}, waiting {} seconds...".format(attempt, backoff)
            )
            await asyncio.sleep(backoff)

        try:
            response = await request_coroutine()
            await response.read()
        except (aiohttp.ClientError, asyncio.exceptions.TimeoutError):
            if attempt == retries - 1:
                raise  # propagate ClientError in case no retries left
        else:
            if response.status not in RETRY_STATUSES:
                return response  # on all non-retry statuses: return response

    return response  # retries exceeded; return the (possibly error) response


async def download_file(
    url: str,
    target: Path,
    chunk_size: int = 16777216,
    timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
    connector: Optional[aiohttp.BaseConnector] = None,
    executor: Optional[ThreadPoolExecutor] = None,
    retries: int = 3,
    backoff_factor: float = 1.0,
    callback_func: Optional[Callable[[int, int], Awaitable[None]]] = None,
) -> Tuple[Path, int]:
    """Download a file to a specified path on disk.

    It is assumed that the file server supports multipart downloads (range
    requests).

    Args:
        url: The url to retrieve.
        target: The location to copy to. If this is an existing file, it is
            overwritten. If it is a directory, a filename is generated from
            the filename in the url.
        chunk_size: The number of bytes per request. Default: 16MB.
        timeout: The total timeout of the download of a single chunk in seconds.
            By default, there is no total timeout, but only socket timeouts of 5s.
        connector: An optional aiohttp connector to support connection pooling.
            If not supplied, a default TCPConnector is instantiated with a pool
            size (limit) of 4.
        executor: The ThreadPoolExecutor to execute local
            file I/O in. If not supplied, default executor is used.
        retries: Total number of retries per request.
        backoff_factor: Multiplier for retry delay times (1, 2, 4, ...)
        callback_func: optional async function used to receive: bytes_downloaded, total_bytes
            for example: async def callback(bytes_downloaded: int, total_bytes: int) -> None

    Returns:
        Tuple of file path, total number of uploaded bytes.

    Raises:
        threedi_api_client.openapi.ApiException: raised on unexpected server
            responses (HTTP status codes other than 206, 413, 429, 503)
        aiohttp.ClientError: various low-level HTTP errors that persist
            after retrying: connection errors, timeouts, decode errors,
            invalid HTTP headers, payload too large (HTTP 413), too many
            requests (HTTP 429), service unavailable (HTTP 503)
    """
    # cast string to Path if necessary
    if isinstance(target, str):
        target = Path(target)

    # if it is a directory, take the filename from the url
    if target.is_dir():
        target = target / urlparse(url)[2].rsplit("/", 1)[-1]

    # open the file
    try:
        async with aiofiles.open(target, "wb", executor=executor) as fileobj:
            size = await download_fileobj(
                url,
                fileobj,
                chunk_size=chunk_size,
                timeout=timeout,
                connector=connector,
                retries=retries,
                backoff_factor=backoff_factor,
                callback_func=callback_func,
            )
    except Exception:
        # Clean up a partially downloaded file
        try:
            await aiofiles.os.remove(target)
        except FileNotFoundError:
            pass
        raise

    return target, size


async def _download_request(client, start, stop, url, timeout, retries, backoff_factor):
    """Send a download with a byte range & parse the content-range header"""
    headers = {"Range": "bytes={}-{}".format(start, stop - 1)}
    request = partial(
        client.request,
        "GET",
        url,
        headers=headers,
        timeout=timeout,
    )
    logger.debug("Downloading bytes {} to {}...".format(start, stop))
    response = await _request_with_retry(request, retries, backoff_factor)
    logger.debug("Finished downloading bytes {} to {}".format(start, stop))
    if response.status == 200:
        raise ApiException(
            status=200,
            reason="The file server does not support multipart downloads.",
        )
    elif response.status != 206:
        raise ApiException(http_resp=response)
    # parse content-range header (e.g. "bytes 0-3/7") for next iteration
    content_range = response.headers["Content-Range"]
    start, stop, total = [
        int(x) for x in CONTENT_RANGE_REGEXP.findall(content_range)[0]
    ]
    return response, total


async def download_fileobj(
    url: str,
    fileobj,
    chunk_size: int = 16777216,
    timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
    connector: Optional[aiohttp.BaseConnector] = None,
    retries: int = 3,
    backoff_factor: float = 1.0,
    callback_func: Optional[Callable[[int, int], Awaitable[None]]] = None,
) -> int:
    """Download a url to a file object using multiple requests.

    It is assumed that the file server supports multipart downloads (range
    requests).

    Args:
        url: The url to retrieve.
        fileobj: The (binary) file object to write into, supporting async I/O.
        chunk_size: The number of bytes per request. Default: 16MB.
        timeout: The total timeout of the download of a single chunk in seconds.
            By default, there is no total timeout, but only socket timeouts of 5s.
        connector: An optional aiohttp connector to support connection pooling.
            If not supplied, a default TCPConnector is instantiated with a pool
            size (limit) of 4.
        retries: Total number of retries per request.
        backoff_factor: Multiplier for retry delay times (1, 2, 4, ...)
        callback_func: optional async function used to receive: bytes_downloaded, total_bytes
            for example: async def callback(bytes_downloaded: int, total_bytes: int) -> None

    Returns:
        The total number of downloaded bytes.

    Raises:
        threedi_api_client.openapi.ApiException: raised on unexpected server
            responses (HTTP status codes other than 206, 413, 429, 503)
        aiohttp.ClientError: various low-level HTTP errors that persist
            after retrying: connection errors, timeouts, decode errors,
            invalid HTTP headers, payload too large (HTTP 413), too many
            requests (HTTP 429), service unavailable (HTTP 503)

        Note that the fileobj might be partially filled with data in case of
        an exception.
    """
    if connector is None:
        connector = aiohttp.TCPConnector(limit=DEFAULT_CONN_LIMIT)

    # Our strategy here is to download the first chunk, get the total file
    # size from the header, and then parrellelize the rest of the chunks.
    # We could get the total Content-Length from a HEAD request, but not all
    # servers support that (e.g. Minio).
    request_kwargs = {
        "url": url,
        "timeout": DEFAULT_DOWNLOAD_TIMEOUT if timeout is None else timeout,
        "retries": retries,
        "backoff_factor": backoff_factor,
    }
    async with aiohttp.ClientSession(connector=connector) as client:
        # start with a single chunk to learn the total file size
        response, file_size = await _download_request(
            client, 0, chunk_size, **request_kwargs
        )

        # write to file
        await fileobj.write(await response.read())
        logger.debug("Written bytes {} to {} to file".format(0, chunk_size))

        if callable(callback_func):
            await callback_func(chunk_size - 1, file_size)

        # return if the file is already completely downloaded
        if file_size <= chunk_size:
            return file_size

        # create tasks for the rest of the chunks
        tasks = [
            asyncio.ensure_future(
                _download_request(client, start, start + chunk_size, **request_kwargs)
            )
            for start in range(chunk_size, file_size, chunk_size)
        ]

        # write the result of the tasks to the file one by one
        try:
            for i, task in enumerate(tasks, 1):
                response, _ = await task
                # write to file
                await fileobj.write(await response.read())
                logger.debug(
                    "Written bytes {} to {} to file".format(
                        i * chunk_size, (i + 1) * chunk_size
                    )
                )
                if callable(callback_func):
                    total: int = (
                        file_size
                        if (i + 1) * chunk_size - 1 > file_size
                        else (i + 1) * chunk_size - 1
                    )
                    await callback_func(total, file_size)
        except Exception:
            # in case of an exception, cancel all tasks
            for task in tasks:
                task.cancel()
            raise

        return file_size


async def upload_file(
    url: str,
    file_path: Path,
    chunk_size: int = 16777216,
    timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
    connector: Optional[aiohttp.BaseConnector] = None,
    md5: Optional[bytes] = None,
    executor: Optional[ThreadPoolExecutor] = None,
    retries: int = 3,
    backoff_factor: float = 1.0,
    callback_func: Optional[Callable[[int, int], Awaitable[None]]] = None,
) -> int:
    """Upload a file at specified file path to a url.

    The upload is accompanied by an MD5 hash so that the file server checks
    the integrity of the file.

    Args:
        url: The url to upload to.
        file_path: The file path to read data from.
        chunk_size: The size of the chunk in the streaming upload. Note that this
            function does not do multipart upload. Default: 16MB.
        timeout: The total timeout of the upload in seconds.
            By default, there is no total timeout, but only socket connect timeout
            of 5 seconds and a socket read timeout of 10 minutes.
        connector: An optional aiohttp connector to support connection pooling.
        md5: The MD5 digest (binary) of the file. Supply the MD5 if you already
            have access to it. Otherwise this function will compute it for you.
        executor: The ThreadPoolExecutor to execute local file I/O and MD5 hashing
            in. If not supplied, default executor is used.
        retries: Total number of retries per request.
        backoff_factor: Multiplier for retry delay times (1, 2, 4, ...)
        callback_func: optional async function used to receive: bytes_uploaded, total_bytes
            for example: async def callback(bytes_uploaded: int, total_bytes: int) -> None

    Returns:
        The total number of uploaded bytes.

    Raises:
        IOError: Raised if the provided file is incompatible or empty.
        threedi_api_client.openapi.ApiException: raised on unexpected server
            responses (HTTP status codes other than 206, 413, 429, 503)
        aiohttp.ClientError: various low-level HTTP errors that persist
            after retrying: connection errors, timeouts, decode errors,
            invalid HTTP headers, payload too large (HTTP 413), too many
            requests (HTTP 429), service unavailable (HTTP 503)
    """
    # cast string to Path if necessary
    if isinstance(file_path, str):
        file_path = Path(file_path)

    # open the file
    async with aiofiles.open(file_path, "rb", executor=executor) as fileobj:
        size = await upload_fileobj(
            url,
            fileobj,
            chunk_size=chunk_size,
            timeout=timeout,
            connector=connector,
            md5=md5,
            executor=executor,
            retries=retries,
            backoff_factor=backoff_factor,
            callback_func=callback_func,
        )

    return size


async def _iter_chunks(
    fileobj,
    chunk_size: int,
    callback_func: Optional[Callable[[int], Awaitable[None]]] = None,
):
    """Yield chunks from a file stream"""
    assert chunk_size > 0
    uploaded_bytes: int = 0
    while True:
        data = await fileobj.read(chunk_size)
        if len(data) == 0:
            break
        uploaded_bytes += chunk_size
        if callable(callback_func):
            await callback_func(uploaded_bytes)
        yield data


async def _compute_md5(
    fileobj,
    chunk_size: int,
    executor: Optional[ThreadPoolExecutor] = None,
):
    """Return the md5 digest for given fileobj."""
    loop = asyncio.get_event_loop()

    await fileobj.seek(0)
    hasher = hashlib.md5()
    async for chunk in _iter_chunks(fileobj, chunk_size=chunk_size):
        # From python docs: the Python GIL is released for data larger than
        # 2047 bytes at object creation or on update.
        # So it makes sense to do the hasher updates in a threadpool.
        await loop.run_in_executor(executor, partial(hasher.update, chunk))
    return await loop.run_in_executor(executor, hasher.digest)


async def _upload_request(
    client,
    fileobj,
    chunk_size,
    callback_func: Optional[Callable[[int, int], Awaitable[None]]],
    *args,
    **kwargs
):
    """Send a request with the contents of fileobj as iterable in the body"""
    file_size: int = await fileobj.seek(0, 2)

    await fileobj.seek(0)

    async def callback(uploaded_bytes: int):
        if callable(callback_func):
            if uploaded_bytes > file_size:
                uploaded_bytes = file_size
            await callback_func(uploaded_bytes, file_size)

    return await client.request(
        *args,
        data=_iter_chunks(fileobj, chunk_size=chunk_size, callback_func=callback),
        **kwargs,
    )


async def upload_fileobj(
    url: str,
    fileobj,
    chunk_size: int = 16777216,
    timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
    connector: Optional[aiohttp.BaseConnector] = None,
    md5: Optional[bytes] = None,
    executor: Optional[ThreadPoolExecutor] = None,
    retries: int = 3,
    backoff_factor: float = 1.0,
    callback_func: Optional[Callable[[int, int], Awaitable[None]]] = None,
) -> int:
    """Upload a file object to a url.

    The upload is accompanied by an MD5 hash so that the file server checks
    the integrity of the file.

    Args:
        url: The url to upload to.
        fileobj: The (binary) file object to read from, supporting async I/O.
        chunk_size: The size of the chunk in the streaming upload. Note that this
            function does not do multipart upload. Default: 16MB.
        timeout: The total timeout of the upload in seconds.
            By default, there is no total timeout, but only socket connect timeout
            of 5 seconds and a socket read timeout of 10 minutes.
        connector: An optional aiohttp connector to support connection pooling.
        md5: The MD5 digest (binary) of the file. Supply the MD5 if you already
            have access to it. Otherwise this function will compute it for you.
        executor: The ThreadPoolExecutor to execute MD5 hashing in. If not
            supplied, default executor is used.
        retries: Total number of retries per request.
        backoff_factor: Multiplier for retry delay times (1, 2, 4, ...)
        callback_func: optional async function used to receive: bytes_uploaded, total_bytes
            for example: async def callback(bytes_uploaded: int, total_bytes: int) -> None

    Returns:
        The total number of uploaded bytes.

    Raises:
        IOError: Raised if the provided file is incompatible or empty.
        threedi_api_client.openapi.ApiException: raised on unexpected server
            responses (HTTP status codes other than 206, 413, 429, 503)
        aiohttp.ClientError: various low-level HTTP errors that persist
            after retrying: connection errors, timeouts, decode errors,
            invalid HTTP headers, payload too large (HTTP 413), too many
            requests (HTTP 429), service unavailable (HTTP 503)
    """
    # There are two ways to upload in S3 (Minio):
    # - PutObject: put the whole object in one time
    # - multipart upload: requires presigned urls for every part
    # We can only do the first option as we have no other presigned urls.
    # So we take the first option, but we do stream the request body in chunks.

    # We will get hard to understand tracebacks if the fileobj is not
    # in binary mode. So use a trick to see if fileobj is in binary mode:
    if not isinstance(await fileobj.read(0), bytes):
        raise IOError(
            "The file object is not in binary mode. Please open with mode='rb'."
        )

    # For computing the MD5 we need to do an extra pass on the file.
    if md5 is None:
        md5 = await _compute_md5(fileobj, chunk_size, executor=executor)

    file_size = await fileobj.seek(0, 2)  # go to EOF to get the file size
    if file_size == 0:
        raise IOError("The file object is empty.")

    # Tested: both Content-Length and Content-MD5 are checked by Minio
    headers = {
        "Content-Length": str(file_size),
        "Content-MD5": base64.b64encode(md5).decode(),
    }

    async with aiohttp.ClientSession(connector=connector) as client:
        request = partial(
            _upload_request,
            client,
            fileobj,
            chunk_size,
            callback_func,
            "PUT",
            url,
            headers=headers,
            timeout=DEFAULT_UPLOAD_TIMEOUT if timeout is None else timeout,
        )
        response = await _request_with_retry(request, retries, backoff_factor)
        if response.status != 200:
            raise ApiException(status=response.status, reason=response.reason)

    return file_size
