import nats
import json

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
    async def add_subscribe(cls, queue, handler):
        async def subscribe_handler(message):
            reply = message.reply
            data = json.loads(message.data.decode())
            response = await handler(data)

            if len(reply):
                await cls.send(reply, response)

        await cls._nats_connection.subscribe(queue, cb=subscribe_handler)

    @classmethod
    async def send(cls, queue, data = {}):
        await cls._nats_connection.publish(
            queue, 
            payload=json.dumps(data).encode(),
        )

    @classmethod
    async def request(cls, queue, data = {}, timeout = 1.0) -> dict:
        response = await cls._nats_connection.request(
            subject=queue,
            payload=json.dumps(data).encode(),
            timeout=timeout,
        )

        return json.loads(response.data.decode())
