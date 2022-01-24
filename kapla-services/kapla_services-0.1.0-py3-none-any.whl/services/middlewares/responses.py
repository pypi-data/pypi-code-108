from __future__ import annotations

from typing import Any, Awaitable, Callable, Iterable, Optional

from loguru import logger

from kapla.services.errors import AbortResponseError
from kapla.services.headers import Headers
from kapla.services.io import dump
from kapla.services.requests import Request
from kapla.services.responses import Response


class ToResponseMiddleware:
    DEFAULT_STATUS_CODE = 200

    def __init__(
        self, status_code: Optional[int] = None, details: Optional[str] = None
    ) -> None:
        self.status_code = status_code or self.DEFAULT_STATUS_CODE
        self.details = details

    async def __call__(
        self, request: Request, dispatch: Callable[..., Awaitable[Any]]
    ) -> Response[Any]:
        """Middleware used to transform any return value into a response."""
        # Execute the wrapped callback
        result = await dispatch(request)
        # Return response directly
        if isinstance(result, Response):
            return result
        # Add a header indicating to whom we're replying
        forward_headers = Headers(
            {
                **request.headers,
                "x-request-origin": str(request.subject),
            }
        )
        # Since we don't use any try/except block here
        # if we got a return value, we consider it a success
        response_data = {
            **forward_headers,
            "success": True,
            "code": self.status_code,
            "data": result,
            "details": self.details,
        }
        response = Response[Any](**response_data)
        logger.trace(f"Gathered response: {response}")
        return response


async def ensure_failure(
    request: Request, dispatch: Callable[..., Awaitable[Response[Any]]]
) -> Response[Any]:
    """Middleware used to catch all exceptions raised in the middleware stack."""
    try:
        response = await dispatch(request)
    # Catch exceptions
    except Exception as err:
        # Fetch the error type
        err_type = type(err)
        # Add a header indicating to whom we're replying
        forward_headers = Headers(
            {
                **request.headers,
                "x-request-origin": str(request.subject),
            }
        )
        response_data = {
            **forward_headers,
            "success": False,
            "error": err_type.__name__,
            "code": 500,
            "details": str(err),
            "exception": err,
        }
        # Create a response
        response = Response[None](**response_data)
        logger.warning(f"Created failed response ({response.get_headers()})")
    # If no error were raised simply return the response
    return response


class ReplyMiddleware:
    def __init__(
        self,
        send: Callable[[Request], Awaitable[None]],
        drop_headers: Iterable[str] = [],
    ) -> None:
        self._send = send
        self._drop_headers = set(drop_headers)

    async def __call__(
        self, request: Request, dispatch: Callable[..., Awaitable[Response[Any]]]
    ) -> Response[Any]:
        """Middleware used to ensure a reply is sent"""
        response = await dispatch(request)
        if response.request_origin is None:
            response.request_origin = str(request.subject)
        # Only reply if the "reply" field is defined on the request
        if request.reply:
            # Forward only headers which are not listed in self._drop_headers attribute
            forward_headers = {
                key: value
                for key, value in request.headers.items()
                if key not in self._drop_headers
            }
            # Generate a request to publish
            response_as_request = Request._from_reply(
                subject=request.reply,
                payload=dump(response.data),
                headers={
                    **forward_headers,
                    **response.get_headers(),
                },
            )
            # Potentially abort
            if response.abort or response_as_request.headers.get("x-abort-response"):
                raise AbortResponseError(
                    "Aborting request due to x-abort-response header"
                )
            # Publish the request
            await self._send(response_as_request)
        # Return response
        return response
