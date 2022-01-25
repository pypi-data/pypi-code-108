import nats
import json

from typing import Union

from pydantic import BaseModel

from eyja.hubs.base_hub import BaseHub
from eyja.hubs.config_hub import ConfigHub
from eyja.utils import random_string


class NATSHub(BaseHub):
    _nats_connection = None

    @classmethod
    async def init(cls):
        servers = []
        nats_config = ConfigHub.get('nats', {})
        if isinstance(nats_config, list):
            for conf in nats_config:
                host = conf.get('host', 'localhost')
                port = conf.get('port', '4222')
                servers.append(f'nats://{host}:{port}')
        else:
            host = nats_config.get('host', 'localhost')
            port = nats_config.get('port', '4222')
            servers.append(f'nats://{host}:{port}')

        cls._nats_connection = await nats.connect(servers=servers)

        await super().init()

    @classmethod
    async def reset(cls):
        if cls._nats_connection is not None:
            await cls._nats_connection.drain()

        await super().reset()

    @classmethod
    async def add_subscribe(cls, queue, handler, data_cls = dict):
        async def subscribe_handler(message):
            reply = message.reply
            data = json.loads(message.data.decode())
            response = await handler(data_cls(**data))

            if len(reply):
                await cls.send(reply, response)

        await cls._nats_connection.subscribe(queue, cb=subscribe_handler)

    @classmethod
    async def add_route(cls, route):
        await cls.add_subscribe(route.queue, route.handler, data_cls=route.data_cls)

    @classmethod
    async def add_route_group(cls, group):
        for route in group.routes:
            await cls.add_route(route)

    @classmethod
    async def send(cls, queue, data: Union[dict, BaseModel] = {}):
        if isinstance(data, dict):
            payload=json.dumps(data).encode()
        else:
            payload=json.dumps(data.dict()).encode()

        await cls._nats_connection.publish(
            queue, 
            payload=payload,
        )

    @classmethod
    async def request(
        cls,
        queue,
        data: Union[dict, BaseModel] = {},
        timeout = 1.0,
        data_cls = dict
    ) -> Union[dict, BaseModel]:
        if isinstance(data, dict):
            payload=json.dumps(data).encode()
        else:
            payload=json.dumps(data.dict()).encode()

        response = await cls._nats_connection.request(
            subject=queue,
            payload=payload,
            timeout=timeout,
        )

        return data_cls(**json.loads(response.data.decode()))
