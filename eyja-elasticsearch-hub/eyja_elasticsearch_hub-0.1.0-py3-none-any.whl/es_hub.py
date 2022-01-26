import os

from urllib.parse import urlparse

from eyja.hubs.base_hub import BaseHub
from eyja.hubs.config_hub import ConfigHub
from elasticsearch import AsyncElasticsearch


class ESHub(BaseHub):
    client: AsyncElasticsearch

    @classmethod
    async def init(cls):
        cls.client = AsyncElasticsearch(hosts=ConfigHub.get('elasticsearch.hosts'))

    @classmethod
    async def create_index(cls, index: str, object_id: str, document: dict):
        await cls.client.index(
            index=index,
            id=object_id,
            document=document,
        )
