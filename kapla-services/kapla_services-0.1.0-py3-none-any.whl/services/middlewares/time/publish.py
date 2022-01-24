from datetime import datetime, timezone
from typing import Awaitable, Callable, TypeVar

from kapla.services.requests import Request
from kapla.services.responses import Response

T = TypeVar("T")


async def x_publish_time(
    request: Request, dispatch: Callable[..., Awaitable[Response[T]]]
) -> Response[T]:
    """Add the xpublish-time header"""
    # Add publish time header
    request.headers["x-publish-time"] = datetime.now(timezone.utc).isoformat()
    # Dispatch request (send the request and wait for a response)
    return await dispatch(request)
