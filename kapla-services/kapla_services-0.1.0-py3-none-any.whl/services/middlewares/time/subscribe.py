from timeit import default_timer
from typing import Awaitable, Callable, TypeVar

from kapla.services.requests import Request
from kapla.services.responses import Response

T = TypeVar("T")


async def x_process_time(
    request: Request, dispatch: Callable[..., Awaitable[Response[T]]]
) -> Response[T]:
    """Accept a request of any type and return the dispatched return value

    This is an example of subscription middleware.
    """
    # Get start time
    start = default_timer()
    # Dispatch request (let the subscription process the request and obtain a response)
    response = await dispatch(request)
    # Get end time
    end = default_timer()
    # Convert duration into milliseconds
    duration_ms = (end - start) * 1000
    # Update process time on response
    response.process_duration = duration_ms
    # Return response
    return response
