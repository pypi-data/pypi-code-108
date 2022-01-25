from typing import List

from pydantic import BaseModel

from .nats_route import NATSRoute


class NATSRouteGroup(BaseModel):
    routes: List[NATSRoute]
