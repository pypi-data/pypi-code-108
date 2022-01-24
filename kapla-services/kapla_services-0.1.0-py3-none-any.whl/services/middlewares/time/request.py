from timeit import default_timer
from typing import Awaitable, Callable, TypeVar

from kapla.services.requests import Request
from kapla.services.responses import Response

T = TypeVar("T")


async def x_request_time(
    request: Request, dispatch: Callable[..., Awaitable[Response[T]]]
) -> Response[T]:
    """Measure total time of request.

    This is an example of request middleware
    """
    # Get start time
    start = default_timer()
    # Dispatch request (send the request and wait for a response)
    response = await dispatch(request)
    # Only consider responses
    if not isinstance(response, Response):
        return response
    # Get end time
    end = default_timer()
    # Convert duration into milliseconds
    duration_ms = (end - start) * 1000
    # Update message headers
    response.request_duration = duration_ms
    # Return untouched reply if type is not Msg or Response
    return response
