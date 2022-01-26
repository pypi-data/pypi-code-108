from eyja.interfaces.plugins import BasePlugin
from eyja.constants.types import PluginTypes

from .es_hub import ESHub


class ESPlugin(BasePlugin):
    name = 'elasticsearch'
    plugin_type = PluginTypes.HUB

    @classmethod
    async def init(cls):
        await ESHub.init()


__all__ = [
    'ESHub',
]
