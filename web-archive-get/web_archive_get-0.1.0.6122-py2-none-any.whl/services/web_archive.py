
import datetime
import json
import time
from urllib import request
from urllib.parse import urljoin
from aiohttp import ClientSession
from requests.models import PreparedRequest
from warcio.archiveiterator import ArchiveIterator
import asyncio
import gzip
from web_archive_get.services.cdx import CDX
from io import BytesIO
import tldextract


class web_archive_url():
    def __init__(self, data):
        self.data = data

    def get_length(self):
        return self.data["length"]

    def get_statuscode(self, roles=[]):
        try:
            return int(self.data["statuscode"])
        except:
            return 200

    def get_mimetype(self, roles=[]):
        try:
            return self.data["mimetype"]
        except:
            return None

    def get_url(self, roles=[]):
        return self.data["original"]

    async def request(self):
        url_dir = urljoin("http://web.archive.org/web/",
                          self.data["timestamp"]) + "/" + self.data["original"]
        async with ClientSession() as client:
            async with client.get(url_dir, timeout=9999999) as response:
                try:
                    return await response.text()
                except:
                    return await response.content.read()


class web_archive(CDX):
    def __init__(self) -> None:
        self.endpoints = [
            "http://web.archive.org/cdx/search/cdx"
        ]

    async def lookup(self, url, params):
        params.append(("output", "json"))
        params.append(("url", url))
        for endpoint in self.endpoints:
            req_page = PreparedRequest()
            req_page.prepare_url(endpoint, params)
            x = []
            async with ClientSession() as client:
                async with client.get(req_page.url, timeout=9999999) as response:
                    data = await response.json()
            for i in data[1:]:
                l = {}
                for count, item in enumerate(data[0], start=0):
                    l[item] = i[count]
                x.append(web_archive_url(l))
        return x


if __name__ == '__main__':
    cc = web_archive()
    loop = asyncio.get_event_loop()
    a = cc.search_url_subpath("www.pirateparty.org.uk/blog/")
    s = loop.run_until_complete(a)
    text = loop.run_until_complete(s[0].request())
    #
