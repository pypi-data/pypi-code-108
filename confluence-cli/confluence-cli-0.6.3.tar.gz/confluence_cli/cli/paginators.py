import logging
from typing import Optional
from urllib.parse import urlparse, parse_qs
from confluence_cli.cli import ConfluenceWrapper

## logger definition
logger = logging.getLogger("confluence_log")


class CloudCQLPaginator(object):
    """
    Pagination changes in cloud from feb-2020
    See https://community.developer.atlassian.com/t/upcoming-changes-to-modernize-search-rest-apis/37746"""

    def __init__(self, confluence: ConfluenceWrapper, cql: str, expand: str, page_size: int):
        """Create a CQLPaginator instance with cql data

        Args:
            confluence (ConfluenceWrapper): [description]
            cql (str): [cql string]
            expand (str): [expand]
            page_size (int): [page size]
        """

        self.confluence = confluence
        self.cql = cql
        self.expand = expand
        self.page_size = page_size
        self.total_size: Optional[int] = None
        self.next_params = None

    def __iter__(self):
        return self

    def __next__(self):
        if self.total_size is None or self.next_params:
            result_page: list = self._get_result_page()

            if result_page:
                return result_page
            else:
                raise StopIteration
        else:
            raise StopIteration

    def _get_result_page(self) -> list:
        if self.next_params:
            resp = self.confluence.get("rest/api/search", params=self.next_params)
        else:
            resp = self.confluence.cql(cql=self.cql, expand=self.expand, limit=self.page_size)
        contents = resp.get("results")
        self.total_size = resp.get("totalSize")
        self.next_params = self._get_params_from_next(resp.get("_links").get("next"))
        if not contents:
            logger.info("Total Size cql: 0")
            self.total_size = 0
        return contents

    @staticmethod
    def _get_params_from_next(url: str) -> Optional[dict]:
        if not url:
            return None
        query = urlparse(url).query
        dl = parse_qs(query)
        d = {key: dl.get(key, [""])[0] for key in dl.keys()}
        return d


class CQLPaginator(object):
    """Use like:
    result_pages = []
    for result_pages in cql_paginator:
        pages.extend(result_pages)
    """

    def __init__(self, confluence: ConfluenceWrapper, cql: str, expand: str, page_size: int):
        """Create a CQLPaginator instance with cql data

        Args:
            confluence (ConfluenceWrapper): [description]
            cql (str): [cql string]
            expand (str): [expand]
            page_size (int): [page size]
        """

        self.confluence = confluence
        self.cql = cql
        self.expand = expand
        self.page_size = page_size
        self.start: int = 0
        self.total_size: Optional[int] = None

    def __iter__(self):
        self.start = 0
        return self

    def __next__(self):
        if self.total_size is None or self.total_size > self.start:
            result_page: list = self._get_result_page()
            self.start += self.page_size
            if result_page:
                return result_page
            else:
                raise StopIteration
        else:
            raise StopIteration

    def _get_result_page(self) -> list:
        contents = self.confluence.cql(cql=self.cql, start=self.start, expand=self.expand, limit=self.page_size)

        if contents:
            # confluence wrapper sets totalSize key inside content (see confluence wrapper cql method)
            self.total_size = int(contents[0].get('totalSize'))
        else:
            logger.info("Total Size cql: 0")
            self.total_size = 0
        return contents


class PagePropertiesPaginator(object):
    def __init__(self, confluence: ConfluenceWrapper, cql: str, space_key: str, page_size: int):
        self.confluence = confluence
        self.total_pages = Optional[int]
        self.current_page = Optional[int]
        self.page_index = 0
        self.cql = cql
        self.space_key = space_key
        self.page_size = page_size

    def __iter__(self):
        self.page_index = 0
        self.total_pages = None
        return self

    def __next__(self):
        if self.total_pages is None or self.total_pages - 1 > self.current_page:
            result_page = self._get_result_page()
            self.page_index += 1
            if result_page:
                return result_page
            else:
                raise StopIteration
        else:
            raise StopIteration

    def _get_result_page(self) -> dict:
        result = self.confluence.get_pages_detail_lines(self.cql, self.space_key, self.page_size, self.page_index)
        self.total_pages: int = result.get("totalPages")
        self.current_page: int = result.get("currentPage")
        return result
