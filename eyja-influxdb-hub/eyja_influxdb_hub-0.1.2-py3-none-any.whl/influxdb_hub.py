from eyja.hubs.base_hub import BaseHub
from eyja.hubs.config_hub import ConfigHub
from aioinflux import InfluxDBClient


class InfluxDBHub(BaseHub):
    @classmethod
    async def init(cls):
        async with InfluxDBClient(**ConfigHub.get('influxdb', {})) as client:
            await client.create_database(ConfigHub.get('influxdb.db', 'test'))

        return await super().init()

    @classmethod
    async def send(cls, data: dict):
        async with InfluxDBClient(**ConfigHub.get('influxdb', {})) as client:
            await client.write(data)
