
import gzip
from io import BytesIO
import json
from pickle import FALSE
from urllib import request
from urllib.parse import urljoin
from aiohttp import ClientSession
from requests.models import PreparedRequest
from warcio.archiveiterator import ArchiveIterator
import asyncio
from web_archive_get.services.cdx import CDX


class common_crawl_index_url():
    def __init__(self, data):
        self.data = data

    def get_length(self):
        return self.data["length"]

    def get_statuscode(self):
        return self.data["statuscode"]

    def get_mimetype(self):
        return self.data["mimetype"]

    def get_url(self):
        return self.data["original"]

    async def request(self):
        print(self.data)
        url_dir = urljoin("https://commoncrawl.s3.amazonaws.com/",
                          self.data["filename"])
        ok = False
        while not ok:
            print("get pages")
            async with ClientSession() as client:
                async with client.get(url_dir, timeout=9999999) as response:
                    if response.ok:
                        ok = response.ok
                        print(response.content)
                        outstr = gzip.decompress(await response.content.read())
                        for record in ArchiveIterator(BytesIO(outstr), arc2warc=True):
                            if record.rec_type == "response":
                                header = {}
                                rec_headers = {}
                                return record.content_stream().read()


class common_crawl_index(CDX):
    def __init__(self) -> None:
        self.endpoints = [
            "https://index.commoncrawl.org/CC-MAIN-2014-49-index"
        ]
        self.setup = False

    async def init_2(self):
        self.endpoints = []
        async with ClientSession() as client:
            async with client.get("https://index.commoncrawl.org/collinfo.json", timeout=9999999) as response:
                for i in await response.json():
                    self.endpoints.append(i["cdx-api"])

    async def lookup(self, url, params):
        if not self.setup:
            self.setup = True
            await self.init_2()
        # RUN IN EVIL MODE
        list_url = []
        async with ClientSession() as client:
            page_f = {}
            params.append(("output", "json"))
            params.append(("url", url))
            for endpoint in self.endpoints:
                req_page = PreparedRequest()
                params.append(("showNumPages", "true"))
                req_page.prepare_url(endpoint, params)
                ok = False
                while not ok:
                    print("trying to get page count: ", req_page.url)
                    async with client.get(req_page.url) as response:
                        if response.ok:

                            page_f = await response.text()

                    ok = response.ok
                params.append(("showNumPages", "false"))
                page_f = json.loads(page_f)
                for pageNum in (range(page_f["pages"])):
                    params.append(("showNumPages", "false"))
                    params.append(("page", pageNum))
                    req_page.prepare_url(endpoint, params)
                    print("trying to get page: ", req_page.url)
                    ok = False
                    while not ok:
                        async with client.get(req_page.url) as response:
                            if response.ok:
                                links = (await response.text()).split("\n")
                                for link in links:
                                    try:
                                        x = json.loads(link)
                                        list_url.append(
                                            common_crawl_index_url(x))
                                    except:
                                        pass
                            ok = response.ok
        return list_url


async def main_1():
    cc = common_crawl_index()

    a = await cc.search_url_subpath("www.pirateparty.org.uk/blog/")
    print(type(await a[0].request()))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    s = loop.run_until_complete(main_1())
