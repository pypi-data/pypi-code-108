from abc import ABC, abstractmethod
from contextlib import ExitStack

from django.http import HttpRequest, HttpResponse


class BaseProfiler(ABC):
    """Base class for custom profilers."""

    @abstractmethod
    def before_request(self, request: HttpRequest, stack: ExitStack):
        """Call on recieve request."""

    @abstractmethod
    def after_request(self, request: HttpRequest, response: HttpResponse):
        """Call after is processed and response available."""
