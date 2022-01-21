
import asyncio
import json
from tkinter import N
from tkinter.messagebox import NO
from urllib import request
from urllib.parse import urljoin
from aiohttp import ClientSession
from requests.models import PreparedRequest
from web_archive_get.services.cdx import CDX


class arquivo_url:
    def __init__(self, data):
        self.data = data

    def get_length(self):
        try:
            return self.data["length"]
        except:
            return None

    def get_statuscode(self):
        try:
            return None
        except:
            return None

    def get_mimetype(self):
        try:
            return self.data["mimetype"]
        except:
            return None

    def get_url(self):
        return self.data["url"]

    async def request(self):
        url_dir = "https://arquivo.pt/wayback/" + \
            self.data["timestamp"] + "/"+self.data["url"]
        async with ClientSession() as client:
            async with client.get(url_dir, timeout=9999999) as response:
                try:
                    return await response.text()
                except:
                    return await response.content.read()


class arquivo(CDX):

    def __init__(self) -> None:
        self.endpoints = ["https://arquivo.pt/wayback/cdx"]

    async def lookup(self, url, params):
        # RUN IN EVIL MODE
        list_url = []
        async with ClientSession() as client:
            params["output"] = "json"
            params["url"] = url
            for endpoint in self.endpoints:
                params["showNumPages"] = "false"
                req_page = PreparedRequest()
                req_page.prepare_url(endpoint, params)
                ok = False
                while not ok:
                    async with client.get(req_page.url) as response:
                        ok = response.ok
                        if response.ok:
                            links = (await response.text()).split("\n")
                            for link in links:
                                try:
                                    x = json.loads(link)
                                    list_url.append(arquivo_url(x))
                                except:
                                    pass
        return list_url


if __name__ == '__main__':
    cc = arquivo()
    loop = asyncio.get_event_loop()
    a = cc.search_url_subpath("www.pirateparty.org.uk/blog/")
    s = loop.run_until_complete(a)
