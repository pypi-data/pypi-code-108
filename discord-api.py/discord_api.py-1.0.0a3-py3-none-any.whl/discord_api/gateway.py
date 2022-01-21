from .guild import Guild
from .dispatch import Dispatch
from .errors import GatewayError
from .interaction import Interaction
import sys
import threading
import asyncio
import time
import aiohttp

class KeepAlive(threading.Thread):
    def __init__(self, *args, **kwargs):
        ws = kwargs.pop("ws", None)
        self.ws = ws
        interval = kwargs.pop("interval", None)
        self.interval = interval
        self._stop_ev = threading.Event()
        super().__init__(target = self.run)
        self.daemon = True
        self._last_ack = time.perf_counter()
        self._last_send = time.perf_counter()
        self._last_recv = time.perf_counter()

    def get_data(self):
        return {
            "op": 1,
            "d": self.ws.sequence
        }

    def run(self):
        while not self._stop_ev.wait(self.interval):
            self.ws.client.print("HEARTBEAT", "send")
            coro = self.ws.send(self.get_data())
            f = asyncio.run_coroutine_threadsafe(coro, loop = self.ws.client.loop)
            while True:
                try:
                    f.result(10)
                    break
                except:
                    pass

class DiscordGateway:
    def __init__(self, client, ws, token):
        self.client = client
        self.ws = ws
        self.token = token
        self.sequence = None
        self.dispatch = Dispatch(client, self)
        self.closed = self.ws.closed

    @classmethod
    async def start_gateway(cls, client, ws, token):
        self = cls(client, ws, token)
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

    async def start(self):
        payload = {
            "op": 2,
            "d": {
                "token": self.token,
                "intents": 513,
                "properties": {
                    "$os": sys.platform,
                    "$browser": "discord-api.py",
                    "$device": "discord-api.py"
                }
            }
        }
        await self.send(payload)

    async def send(self, data:dict):
        await self.ws.send_json(data)

    async def catch_message(self):
        async for msg in self.ws:
            if msg.type is aiohttp.WSMsgType.TEXT:
                await self.event_catch(msg)
            elif msg.type is aiohttp.WSMsgType.ERROR:
                raise msg.data

    async def event_catch(self, msg):
        data = msg.json()
        self.client.dispatch("gateway_response", data)
        if data["op"] != 0:
            if data["op"] == 10:
                self.interval = data["d"]['heartbeat_interval'] / 1000.0
                self.keepalive = KeepAlive(ws = self, interval = self.interval)
                await self.send(self.keepalive.get_data())
                self.keepalive.start()
                self.client.print("HEARTBEAT", "start")
                await self.start()
            if data["op"] == 1:
                await self.send(self.keepalive.get_data())
                
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
