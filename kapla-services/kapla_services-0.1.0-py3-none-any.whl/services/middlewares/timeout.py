from __future__ import annotations

from contextlib import AsyncExitStack
from datetime import datetime, timedelta, timezone
from types import TracebackType
from typing import Any, Awaitable, Callable, Optional, Type

from anyio import move_on_after

from kapla.services.errors import TimeoutError
from kapla.services.requests import Request
from kapla.services.responses import Response


class ProcessTimeoutScope:
    def __init__(self, request: Request) -> None:
        # Number of milliseconds before throwing an error
        timeout = request.process_timeout
        start = request.publish_time
        # Let's get a delay from timeout and start values
        delay: Optional[float]
        # If we got both timeout and start we can compute an allowed delay
        if timeout and start:
            delay_timedelta = timedelta(seconds=timeout) - (
                datetime.now(timezone.utc) - start
            )
            delay = delay_timedelta.total_seconds()
        # Else we can only use the timeout
        else:
            delay = timeout
        # Check if delay is not already expired
        if delay is not None and delay <= 0:
            raise TimeoutError(f"Reached timeout ({timeout:.3f}s)")
        # Store the delay for later usage
        self.delay = delay

    async def __aenter__(self) -> ProcessTimeoutScope:
        """Reference: https://anyio.readthedocs.io/en/stable/cancellation.html#avoiding-cancel-scope-stack-corruption"""
        # Create a cancel scope
        self._cancel_scope = move_on_after(self.delay)
        # Create an exit stack
        self._exitstack = AsyncExitStack()
        # Enter the exit stack
        await self._exitstack.__aenter__()
        # Enter the fail_after context using the exit stack
        self._cancel_scope = self._exitstack.enter_context(self._cancel_scope)
        # Return the instance
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException],
        exc_val: BaseException,
        exc_tb: Optional[TracebackType],
    ) -> bool:
        """Reference: https://anyio.readthedocs.io/en/stable/cancellation.html#avoiding-cancel-scope-stack-corruption"""
        return await self._exitstack.__aexit__(exc_type, exc_val, exc_tb)

    @property
    def cancelled(self) -> bool:
        return self._cancel_scope.cancel_called


# Create a middleware to ensure process timeout
async def ensure_process_timeout(
    request: Request, dispatch: Callable[..., Awaitable[Response[Any]]]
) -> Response[Any]:
    """Middleware used to ensure a process timeout is enfored"""
    try:
        scope = ProcessTimeoutScope(request)
    except TimeoutError:
        msg = f"Process did not start before {request.process_timeout:.3f}s"
        return Response(
            success=False,
            code=504,
            error="ProcessTimeoutError",
            exception=TimeoutError(msg),
            details=msg,
        )
    # Ensure a timeout is raised if processing takes too much time
    async with scope:
        response = await dispatch(request)

    # If we did not process in time
    if scope.cancelled:
        msg = f"Process did not complete before {request.process_timeout:.3f}s"
        return Response(
            success=False,
            code=504,
            error="ProcessTimeoutError",
            exception=TimeoutError(msg),
            details=msg,
        )

    return response
