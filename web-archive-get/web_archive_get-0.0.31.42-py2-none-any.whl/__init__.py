"""
web_archive_get.

An example python library.
"""

__version__ = "0.0.31.4"
__author__ = 'Willdor'
__credits__ = ''
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
