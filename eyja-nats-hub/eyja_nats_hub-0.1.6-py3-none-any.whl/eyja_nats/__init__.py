from eyja.interfaces.plugins import BasePlugin
from eyja.constants.types import PluginTypes

from .nats_hub import NATSHub
from .nats_route_group import (
    NATSRoute,
    NATSRouteGroup,
)


class NATSPlugin(BasePlugin):
    name = 'nats'
    plugin_type = PluginTypes.HUB

    @classmethod
    async def init(cls):
        await NATSHub.init()


__all__ = [
    'NATSHub',
    'NATSRoute',
    'NATSRouteGroup',
]
