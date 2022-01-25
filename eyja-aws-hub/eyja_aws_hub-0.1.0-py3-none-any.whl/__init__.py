from eyja.interfaces.plugins import BasePlugin
from eyja.constants.types import PluginTypes

from .aws_hub import AWSHub


class AWSPlugin(BasePlugin):
    name = 'aws'
    plugin_type = PluginTypes.HUB

    @classmethod
    async def init(cls):
        await AWSHub.init()


__all__ = [
    'AWSHub',
]
