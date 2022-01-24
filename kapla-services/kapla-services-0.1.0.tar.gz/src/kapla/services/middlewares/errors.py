from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Type

from loguru import logger

from kapla.services.requests import Request
from kapla.services.responses import Response


class ErrorHandlerMiddleware:
    """Middleware used to apply error_handlers."""

    def __init__(
        self,
        error_handlers: Dict[
            Type[Exception], Callable[[Exception, Request], Awaitable[Any]]
        ] = {},
    ) -> None:
        self.error_handlers = error_handlers

    async def __call__(
        self, request: Request, dispatch: Callable[..., Awaitable[Any]]
    ) -> Any:
        try:
            result = await dispatch(request)
        except Exception as err:
            # Fetch the error type
            err_type = type(err)
            # If we got a handler
            if err_type in self.error_handlers:
                # Return the result of the error handler
                return await self.error_handlers[err_type](err, request)
            # We do not want to check each exception manually
            # Only Exception can be used to catch all exceptions
            elif Exception in self.error_handlers:
                return await self.error_handlers[Exception](err, request)
            logger.warning("An error not was not handled by ErrorHandlerMiddleware")
            # Else we raise the error
            raise
        # Return the result
        return result


async def catch_low_level_exceptions(
    request: Request, dispatch: Callable[..., Awaitable[Response[Any]]]
) -> Response[Any]:
    """Middleware used to catch exceptions which were not handled"""
    try:
        response = await dispatch(request)
    except Exception as err:
        # FIXME: What do we do in such cases ?
        # At the moment let's just raise the exception, but this should not be tolerated in production
        logger.exception(f"Failed to process request: {request.scope}")
        err_type = type(err).__name__
        return Response(success=False, code=500, error=err_type, details=str(err))

    return response
