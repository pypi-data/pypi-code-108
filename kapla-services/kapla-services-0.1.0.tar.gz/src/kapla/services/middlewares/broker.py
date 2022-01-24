from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable

from kapla.services.requests import Request

if TYPE_CHECKING:  # pragma: no cover
    from kapla.services.broker import Broker  # pragma: no cover


class InjectBrokerMiddleware:
    """Inject broker instance into each request"""

    def __init__(self, broker: Broker) -> None:
        self.broker = broker

    async def __call__(
        self, request: Request, dispatch: Callable[..., Awaitable[Any]]
    ) -> Any:
        request.scope["broker"] = self.broker
        return await dispatch(request)
