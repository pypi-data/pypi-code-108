from eyja.hubs.base_hub import BaseHub
from eyja.hubs.config_hub import ConfigHub
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


class InfluxDBHub(BaseHub):
    bucket: str
    org: str
    client: InfluxDBClient

    @classmethod
    async def init(cls):
        host = ConfigHub.get('influxdb.host')
        token = ConfigHub.get('influxdb.token')
        cls.org = ConfigHub.get('influxdb.org')
        cls.bucket = ConfigHub.get('influxdb.bucket')

        cls.client = InfluxDBClient(
            url=host,
            token=token,
        )

        return await super().init()

    @classmethod
    async def send(cls, data):
        write_api = cls.client.write_api(write_options=SYNCHRONOUS)

        point = Point(data.measurement)

        for tag_name, tag_value in data.tags.items():
            point = point.tag(tag_name, tag_value)

        for field_name, field_value in data.fields.items():
            point = point.field(field_name, field_value)

        point = point.time(data.time, WritePrecision.NS)

        write_api.write(cls.bucket, cls.org, point)
