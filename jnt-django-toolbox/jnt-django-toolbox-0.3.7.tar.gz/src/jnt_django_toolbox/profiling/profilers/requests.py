import time

from jnt_django_toolbox.profiling.profilers.base import BaseProfiler


class RequestsProfiler(BaseProfiler):
    """Request profiler."""

    def __init__(self, header_prefix: str = "app_req"):
        """Initializing."""
        self._header_prefix = header_prefix

    def before_request(self, request, stack):
        """Start capturing requests."""
        self._start_time = time.time()

    def after_request(self, request, response):
        """Add profiling info to response."""
        response[self._header("time")] = round(
            time.time() - self._start_time,
            3,
        )

    def _header(self, name: str) -> str:
        return "{0}_{1}".format(self._header_prefix, name)
