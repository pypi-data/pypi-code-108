from typing import List


class EsRequest:
    _search_term: str
    _filters: List[str]
    _aggregation: bool
    _page: int
    _size: int
    _with_analytics: bool

    def __init__(self, search_term: str, filters: List[str] = None,
                 aggregation: bool = False, page: int = 1, size: int = 10, with_analytics: bool = False):
        """
        A class used to wrap all necessary input for the search endpoint.

        :param search_term: a query which follows Lucene syntax
        :param filters: filters applied on the query
        :param aggregation: indicate if the result should be aggregated or not
        :param page: number of page
        :param size: number of item per page
        :param with_analytics: indicate if the result should have analytics or not
        """
        self._search_term = search_term
        self._filters = filters
        self._aggregation = aggregation
        self._page = page
        self._size = size
        self._with_analytics = with_analytics

    @property
    def search_term(self):
        return self._search_term

    @property
    def filters(self):
        return self._filters

    @property
    def aggregation(self):
        return self._aggregation

    @property
    def page(self):
        return self._page

    @property
    def size(self):
        return self._size

    @property
    def with_analytics(self):
        return self._with_analytics
