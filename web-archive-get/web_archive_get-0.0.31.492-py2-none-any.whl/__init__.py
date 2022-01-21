"""
web_archive_get.

An example python library.
"""

__version__ = "0.0.31.47"
__author__ = 'Willdor'
__credits__ = ''

from web_archive_get.services.archive import archive
from web_archive_get.services.common_crawl_index import common_crawl_index
from web_archive_get.services.web_archive import web_archive
from web_archive_get.services.arquivo import arquivo

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
