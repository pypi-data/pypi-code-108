import sys
import aiohttp
import threading
import asyncio
import time

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
    def __init__(self, ws, **kwargs):
        self.ws = ws
        self.token = kwargs.pop("token")
        self.closed = self.ws.closed
        self.intents = 513
        
    @classmethod
    async def start_gateway(cls, ws, token):
        self = cls(ws, token = token)
        return self

    async def login(self):
        payload = {
            "op": 2,
            "d": {
                "token": self.token,
                "intents": self.intents,
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
                
    async def callback(self, *args, **kwargs):
        pass
                
    async def event_catch(self, msg):
        data = msg.json()
        self.sequence = data["s"]
        if data["op"] != 0:
            if data["op"] == 10:
                self.interval = data["d"]['heartbeat_interval'] / 1000.0
                self.keepalive = KeepAlive(ws = self, interval = self.interval)
                await self.send(self.keepalive.get_data())
                self.keepalive.start()
                await self.login()
            elif data["op"] == 1:
                await self.send(self.keepalive.get_data())
        else:
            await self.callback(data)
