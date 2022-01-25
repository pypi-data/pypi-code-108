import os
import httpx

from urllib.parse import urlparse

from eyja.hubs.base_hub import BaseHub
from eyja.hubs.config_hub import ConfigHub
from aiobotocore.session import get_session


class AWSHub(BaseHub):
    @classmethod
    async def put_file(cls, filepath: str, filecontent: bytes, bucket = None):
        session = get_session()
        async with session.create_client(
            's3', region_name = ConfigHub.get('aws.region', 'us-east-1'),
            aws_secret_access_key = ConfigHub.get('aws.secret_key'),
            aws_access_key_id = ConfigHub.get('aws.access_key'),
            endpoint_url = ConfigHub.get('aws.endpoint')
        ) as s3:
            await s3.put_object(
                Bucket = bucket if bucket else ConfigHub.get('aws.s3.bucket'),
                Key=filepath,
                Body=filecontent
            )

    @classmethod
    async def put_file_from_url(cls, url: str, dirpath: str, filename: str = None, bucket = None):
        if not filename:
            filename = os.path.basename(urlparse(url).path)

        key = f'{dirpath}/{filename}'

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.get(url)

        await cls.put_file(key, resp.content, bucket=bucket)
