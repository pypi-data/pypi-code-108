"""
web_archive_get.

An example python library.
"""

__version__ = "0.1.0.5"
__author__ = 'Willdor'
__credits__ = ''

from web_archive_get.services.archive import archive
from web_archive_get.services.common_crawl_index import common_crawl_index
from web_archive_get.services.web_archive import web_archive
from web_archive_get.services.arquivo import arquivo

__archive = archive()
__web_archive = web_archive()
__arquivo = arquivo()
__cc = common_crawl_index()
__archive_list = [
    __archive,
    __web_archive,
    __arquivo,
    # cc
]

setup = False


async def list_page(url, roles=[[]], archive_list=__archive_list):
    for role in roles:
        for i in archive_list:
            async for x in i.list_page(url, role):
                yield x


async def list_subdoamin(url, roles=[[]], archive_list=__archive_list):
    for role in roles:
        for i in archive_list:
            async for x in i.list_subdoamin(url, role):
                yield x


async def search_url_host(url, roles=[[]], archive_list=__archive_list):
    for role in roles:
        for i in archive_list:
            async for x in i.search_url_host(url, role):
                yield x


async def search_url_subpath(url, roles=[[]], archive_list=__archive_list):
    for role in roles:
        for i in archive_list:
            async for x in i.search_url_subpath(url, role):
                yield x


async def emulate_WebRequests(objs, callback):
    for i in objs:
        pass


async def emulate_WebRequest(obj, callback):
    pass
