from statistics import mean

from django.db import connection
from django.test.utils import CaptureQueriesContext

from jnt_django_toolbox.profiling.profilers.base import BaseProfiler


class DatabaseQueriesProfiler(BaseProfiler):
    """Database queries count profiler."""

    def __init__(self, header_prefix: str = "app_db"):
        """Initializing."""
        self._header_prefix = header_prefix

    def before_request(self, request, stack):
        """Start capturing requests."""
        self._context = CaptureQueriesContext(connection)
        stack.enter_context(self._context)

    def after_request(self, request, response):
        """Add profiling info to response."""
        query_timings = [float(query["time"]) for query in self._context]
        if query_timings:
            response[self._header("total_time")] = round(sum(query_timings), 3)
            response[self._header("max_time")] = round(max(query_timings), 3)
            response[self._header("avg_time")] = round(mean(query_timings), 3)

        response[self._header("count")] = len(self._context)

    def _header(self, name: str) -> str:
        return "{0}_{1}".format(self._header_prefix, name)
