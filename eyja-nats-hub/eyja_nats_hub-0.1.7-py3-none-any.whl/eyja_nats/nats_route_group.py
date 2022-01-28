from typing import Callable, Any, List, Optional

from pydantic import BaseModel

from .nats_route import NATSRoute


class NATSRouteGroup(BaseModel):
    routes: Optional[List[NATSRoute]] = []

    def add_route(self, queue: str, handler: Callable, data_cls: Any = None):
        self.routes.append(
            NATSRoute(
                queue=queue,
                handler=handler,
                data_cls=data_cls,
            )
        )

    def queue(self, queue: str, data_cls: Any = None):
        def decorator(func):
            self.add_route(queue, func, data_cls)
            return func
        return decorator
