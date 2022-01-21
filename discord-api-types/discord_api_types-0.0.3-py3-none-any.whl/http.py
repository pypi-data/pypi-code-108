from aiohttp import ClientSession
from asyncio import get_event_loop, sleep
from .gateway import DiscordGateway
from .errors import ApiError
import asyncio

class HttpClient:
    def __init__(self, loop:asyncio.AbstractEventLoop = None, intents:int = 513, log:bool = True):
        self.log = log
        self.intents = intents
        self.baseurl = "https://discord.com/api/v9"
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.ws = None
        self.session = ClientSession(loop = self.loop)

    def print(self, name, content):
        if self.log is True:
            print(f"[{name}]:{content}")
            
    async def json_or_text(self, r):
        if r.headers["Content-Type"] == "application/json":
            return await r.json()
        
    async def ws_connect(self, url):
        return await self.session.ws_connect(url)
    
    async def login(self):
        return await self.request("GET", "/users/@me")
    
    async def request(self, method:str, path:str, *args, **kwargs):
        headers = {
            "Authorization": f"Bot {self.token}"
        }
        if kwargs.get("json"):
            headers["Content-Type"] = "application/json"
        kwargs["headers"] = headers
        for t in range(5):
            async with self.session.request(method, self.baseurl + path, *args, **kwargs) as r:
                if r.status == 429:
                    data = await r.json()
                    if data["global"] is True:
                        raise ApiError("Now api is limit. Wait a minute please.")
                    else:
                        await sleep(data["retry_after"])
                elif r.status == 404:
                    raise ApiError("Not Found Error")
                elif 300 > r.status >= 200:
                    return await self.json_or_text(r)
        
    async def connect(self):
        if self.ws is None:
            self.ws = await DiscordGateway.start_gateway(self)
            await self.ws.catch_message()
            while not self.ws.closed:
                await self.ws.catch_message()
