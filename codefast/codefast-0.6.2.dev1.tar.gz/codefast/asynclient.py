#!/usr/bin/env python
import asyncio
import json
import aiohttp

class AsyncClient(object):
    def __init__(self, url, loop=None):
        self.url = url
        self.loop = loop or asyncio.get_event_loop()

    async def get(self, url):
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url,
                                   proxy="http://localhost:8234") as response:
                return await response.text()

    async def post(self, url, data):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                return await response.text()

    async def post_with_session(self, session, url, data):
        """Different from the above method, this method will reuse aiohttp.ClientSession"""
        async with session.post(url, data=data) as response:
            return await response.text()

    async def get_with_session(self, session, url):
        async with session.get(url) as response:
            return await response.text()

    async def concurrent_get(self, urls):
        """ This method will use aiohttp.ClientSession to make multiple requests"""
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_with_session(session, url) for url in urls]
            return await asyncio.gather(*tasks)

    async def concurrent_post(self, urls, data):
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.post_with_session(session, url, data) for url in urls
            ]
            return await asyncio.gather(*tasks)

    async def main(self):
        resp = await self.concurrent_get([self.url] * 10)
        for rp in resp:
            print(json.loads(rp))
        print(len(resp))

if __name__ == '__main__':
    import base64
    b64url='aHR0cHM6Ly9pcGluZm8uaW8vanNvbj90b2tlbj03NzJjNGFmMDdhZTUxZgo='
    url = base64.b64decode(b64url).decode('utf-8').rstrip('\n')
    client = AsyncClient(url)
    asyncio.run(client.main())
