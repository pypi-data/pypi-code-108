from eyja.interfaces.plugins import BasePlugin
from eyja.constants.types import PluginTypes

from .influxdb_hub import InfluxDBHub


class InfluxDBPlugin(BasePlugin):
    name = 'influxdb'
    plugin_type = PluginTypes.HUB

    @classmethod
    async def init(cls):
        await InfluxDBHub.init()


__all__ = [
    'InfluxDBHub',
]
