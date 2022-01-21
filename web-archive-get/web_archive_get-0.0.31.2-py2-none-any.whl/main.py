from functools import cache
from services.archive import archive
from services.common_crawl_index import common_crawl_index
from services.web_archive import web_archive
from services.arquivo import arquivo

cc = common_crawl_index()
archive_list = [
    archive(),
    web_archive(),
    arquivo(),
    # cc
]

setup = False


async def list_page(url, roles=[]):
    for i in archive_list:
        async for x in i.list_page(url):
            yield x


async def list_subdoamin(url, roles=[]):
    for i in archive_list:
        async for x in i.list_subdoamin(url):
            yield x


async def search_url_host(url, roles=[]):
    for i in archive_list:
        async for x in i.search_url_host(url):
            yield x


async def search_url_subpath(url, roles=[]):
    for i in archive_list:
        async for x in i.search_url_subpath(url):
            yield x


async def emulate_WebRequests(objs, callback):
    for i in objs:
        pass


async def emulate_WebRequest(obj, callback):
    pass
