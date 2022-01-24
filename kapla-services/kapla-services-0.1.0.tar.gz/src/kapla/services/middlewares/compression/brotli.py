from typing import Any, Awaitable, Callable, Optional

from brotli import compress, decompress

from kapla.services.io import dump
from kapla.services.requests import Request
from kapla.services.responses import Response


async def listen_brotly_encoding(
    request: Request, dispatch: Callable[..., Awaitable[Optional[Response[Any]]]]
) -> Optional[Response[bytes]]:
    """Decompress data when receiving requests and compress before sending response data"""
    # See https://developer.mozilla.org/fr/docs/Web/HTTP/Headers/Content-Encoding
    if request.data and request.headers.get("content-encoding", None) == "br":
        # FIXME: Should we run this in an executor ?
        # Brotli releases the GIL when compressing/decompressing, so it should be safe/performant to use threads
        # But in this case, we should make sure that data holds at least "decompress_min_size" bytes so that we're not wasting time spawning a new task
        request.scope["data"] = decompress(request.data)
    # Dispatch request
    response = await dispatch(request)
    # If we got a response, we compress the response data
    if response and response.data and response.content_encoding in ("br", None):
        # First dump into bytes then compress using brotly algorithm
        response.data = compress(dump(response.data))
        # Set content_encoding
        response.content_encoding = "br"
    # Return response (or None)
    return response


async def send_brotly_encoding(
    request: Request, dispatch: Callable[..., Awaitable[Optional[Response[Any]]]]
) -> Optional[Response[Any]]:
    """Compress data when sending requests and decompress before returning response"""
    # See https://developer.mozilla.org/fr/docs/Web/HTTP/Headers/Content-Encoding
    # Only set content-encoding if it's not already set
    if request.headers.get("content-encoding") in ("br", None):
        request.headers["content-encoding"] = "br"
        # FIXME: Should we run this in an executor ?
        # Brotli releases the GIL when compressing/decompressing, so it should be safe/performant to use threads
        # But in this case, we should make sure that data holds at least "decompress_min_size" bytes so that we're not wasting time spawning a new task
        request.scope["data"] = compress(dump(request.data))
    # Dispatch request (send the request and maybe receive a response)
    response = await dispatch(request)
    # If we got a response with the same content-type, decompress response data
    if response and response.data and response.content_encoding == "br":
        # First dump into bytes then compress using brotly algorithm
        response.data = decompress(response.data)
    # Return response (or None)
    return response
