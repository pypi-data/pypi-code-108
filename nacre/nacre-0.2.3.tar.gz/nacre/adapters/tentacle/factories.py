import asyncio

from nautilus_trader.cache.cache import Cache
from nautilus_trader.common.clock import LiveClock
from nautilus_trader.common.logging import LiveLogger
from nautilus_trader.live.factories import LiveDataClientFactory

# from nautilus_trader.model.identifiers import TraderId
from nautilus_trader.msgbus.bus import MessageBus

from nacre.adapters.tentacle.data import TentacleDataClient


class TentacleDataClientFactory(LiveDataClientFactory):
    @staticmethod
    def create(
        loop: asyncio.AbstractEventLoop,
        name: str,
        config,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
        logger: LiveLogger,
        client_cls=None,
    ):

        host = config.get("gateway_host", "localhost")
        port = config.get("gateway_port", 9999)

        grpc_endpoint = f"{host}:{port}"

        return TentacleDataClient(
            loop=loop,
            grpc_endpoint=grpc_endpoint,
            msgbus=msgbus,
            cache=cache,
            clock=clock,
            logger=logger,
        )
