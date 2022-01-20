from contextlib import ExitStack

from django.conf import settings


class ProfilingMiddleware:
    """Middleware for providing profiling info."""

    def __init__(self, get_response):
        """Initializing."""
        self._get_response = get_response
        self._profilers = settings.REQUEST_PROFILERS or []

    def __call__(self, request):
        """Handle request."""
        with ExitStack() as stack:
            for profiler in self._profilers:
                profiler.before_request(request, stack)

            response = self._get_response(request)
            for profiler in self._profilers:
                profiler.after_request(request, response)

        return response
