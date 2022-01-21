import asyncio

class Dispatch:
    def __init__(self, client, gateway):
        self.client = client
        self.gateway = gateway
        self.dispatch = client.dispatch

    async def filter(self, data):
        name, data = data["t"], data["d"]
        if name == "INTERACTION_CREATE":
            print(data)

    async def call_ready(self):
        while True:
            try:
                self.gateway._ready_state = self.client.loop.create_future()
                await asyncio.wait_for(self.gateway._ready_state, timeout = 2)
            except asyncio.TimeoutError:
                break
        self.dispatch("ready")
