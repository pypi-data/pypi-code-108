from .guild import Guild
from .dispatch import Dispatch
from .errors import GatewayError
from .interaction import Interaction
from discord_api_types import DiscordGateway
import sys
import threading
import asyncio
import time
import aiohttp

class DiscordGateway(DiscordGateway):
    def __init__(self, client, ws, token):
        super().__init__(ws, token = token)
        self.client = client
        self.ws = ws
        self.sequence = None
        self.dispatch = Dispatch(client, self)
        self.closed = self.ws.closed

    @classmethod
    async def start_gateway(cls, client, ws, token):
        self = cls(client, ws, token = token)
        await self.catch_message()
        return self

    async def reconnect(self):
        if self.ws is None:
            raise GatewayError("You isn't connect to gateway.")
        else:
            self.ws = None
            self.keepalive = None
            self.ws = await self.client.http.ws_connect("wss://gateway.discord.gg")
            await self.catch_message()

    async def callback(self, data):
        if data["t"] == "READY":
            self.sequence = data["s"]
            await self.dispatch.call_ready()
                
        if data["t"] == "GUILD_CREATE":
            self._ready_state.cancel()
            guild = Guild.from_dict(self.client, data["d"])
            self.client.guilds.append(guild)
                
        elif data["t"] == "INTERACTION_CREATE":
            interaction = Interaction.from_dict(self.client, data["d"])
            self.client.dispatch("interaction", interaction)

        elif data["t"] == "MESSAGE_CREATE":
            pass
            # message = Message.from_dict(client, data["d"])
            # self.client.dispatch("message", message)

class VoiceGateway(DiscordGateway):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
