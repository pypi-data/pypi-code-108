import asyncio
from aiohttp import ClientSession
from requests.models import PreparedRequest
import re


class archive_url():
    def __init__(self, data):
        self.data = data

    async def request(self):
        async with ClientSession() as client:
            async with client.get(self.data["href"], timeout=9999999) as response:
                return response.text()

    def get_length(self):
        return self.data["length"]

    def get_statuscode(self):
        return None

    def get_mimetype(self):
        print("DEBUG:", self.data)
        try:
            return self.data["mimetype"]
        except:
            return None

    def get_url(self):
        return self.data["original"]


class archive():
    def __init__(self) -> None:
        self.__can_filter = False
        self.endpoint = "http://archive.is"

    async def list_page(self, url, roles=[]):
        alist = []
        reg = '<([0-z:\/.]+)>; rel="([a-z ]*)"; datetime="([0-z, ]*)"'
        params = "http://archive.is/timemap/" + url
        async with ClientSession() as client:
            async with client.get(params) as response:
                texts = (await response.text())
                m = re.finditer(reg, texts)
                for i in m:
                    yield archive_url({"href": i.group(1), "rel": i.group(2), "datetime": i.group(3)})

    async def list_subdoamin(self, url, roles={}):
        yield

    async def search_url_host(self, url, roles={}):
        yield

    async def search_url_subpath(self, url, roles={}):
        yield

    async def lookup(url, params):
        yield


if __name__ == '__main__':
    cc = archive()
    loop = asyncio.get_event_loop()
    a = cc.list_page("http://www.w3.org/TR/webarch/")
    s = loop.run_until_complete(a)
