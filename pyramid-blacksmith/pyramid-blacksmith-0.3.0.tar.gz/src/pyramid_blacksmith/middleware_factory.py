"""Middleware"""
import abc
from typing import Dict

from blacksmith import SyncHTTPAddHeadersMiddleware, SyncHTTPMiddleware
from pyramid.request import Request  # type: ignore


class AbstractMiddlewareFactoryBuilder(abc.ABC):
    """Build the factory"""

    @abc.abstractmethod
    def __call__(self, request: Request) -> SyncHTTPMiddleware:
        """Called on demand per request to build a client with this middleware"""


class ForwardHeaderFactoryBuilder(AbstractMiddlewareFactoryBuilder):
    """
    Forward headers (every keys in kwargs)

    :param kwargs: headers
    """

    def __init__(self, **kwargs: Dict[str, bool]):
        self.headers = list(kwargs.keys())

    def __call__(self, request: Request) -> SyncHTTPAddHeadersMiddleware:
        headers: Dict[str, str] = {}
        for hdr in self.headers:
            val = request.headers.get(hdr)
            if val:
                headers[hdr] = val
        return SyncHTTPAddHeadersMiddleware(headers)
