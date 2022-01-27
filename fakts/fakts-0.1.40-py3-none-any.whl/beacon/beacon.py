from typing import List
from pydantic import BaseModel
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST
import asyncio
import json
from koil import koil
import logging


logger = logging.getLogger(__name__)


class FaktsEndpoint(BaseModel):
    url: str = "http://localhost/setupapp"
    name: str = "default"


class BeaconProtocol(asyncio.DatagramProtocol):
    pass


class EndpointBeacon:
    BIND = ""
    BROADCAST_PORT = 45678
    BROADCAST_ADDRESS = "<broadcast>"
    MAGIC_PHRASE = "beacon-fakts"

    def __init__(
        self,
        broadcast_port=None,
        bind=None,
        magic_phrase=None,
        broadcast_adress=None,
        advertised_endpoints: List[FaktsEndpoint] = [],
        interval=1,
    ) -> None:
        self.broadcast_port = broadcast_port or self.BROADCAST_PORT
        self.bind = bind or self.BIND
        self.magic_phrase = magic_phrase or self.MAGIC_PHRASE
        self.broadcast_adress = broadcast_adress or self.BROADCAST_ADDRESS

        self.advertised_endpoints = advertised_endpoints
        assert len(self.advertised_endpoints) > 0, "No config points provided"
        self.interval = interval

    def endpoint_to_message(self, config: FaktsEndpoint):
        return bytes(self.magic_phrase + json.dumps(config.dict()), "utf8")

    async def arun(self):

        s = socket(AF_INET, SOCK_DGRAM)  # create UDP socket
        s.bind((self.bind, 0))
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)  # this is a broadcast socket

        loop = asyncio.get_event_loop()
        transport, pr = await loop.create_datagram_endpoint(BeaconProtocol, sock=s)

        messages = [
            self.endpoint_to_message(config) for config in self.advertised_endpoints
        ]

        while True:
            for message in messages:
                transport.sendto(message, (self.broadcast_adress, self.broadcast_port))
                logger.info(f"Send Message {message}")

            await asyncio.sleep(self.interval)

    def run(self):
        return koil(self.arun())
