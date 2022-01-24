import re
from opentelemetry.semconv.trace import SpanAttributes

from helios.instrumentation.base_http_instrumentor import HeliosBaseHttpInstrumentor


class HeliosTornadoInstrumentor(HeliosBaseHttpInstrumentor):
    CLASS_NAME = 'TornadoInstrumentor'
    MODULE_NAME = 'opentelemetry.instrumentation.tornado'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.CLASS_NAME)

    def instrument(self, tracer_provider=None):
        if self.get_instrumentor() is None:
            return

        self.get_instrumentor().instrument(server_request_hook=self.server_request_hook,
                                           tracer_provider=tracer_provider)

    def server_request_hook(self, span, handler):
        if handler.request is None:
            return

        route = self.extract_http_route(handler)
        span.set_attribute(SpanAttributes.HTTP_ROUTE, route) if route else None
        span.set_attribute(SpanAttributes.HTTP_URL, handler.request.full_url())
        request_payload = None if handler.request.body is None else handler.request.body.decode('utf-8')
        HeliosBaseHttpInstrumentor.base_request_hook(span, handler.request.headers, request_payload)

    @staticmethod
    def extract_http_route(handler):
        if (
                handler.application is None or
                handler.application.wildcard_router is None or
                handler.application.wildcard_router.rules is None or
                handler.request is None or
                handler.request.path is None
        ):
            return None

        for rule in handler.application.wildcard_router.rules:
            # noinspection PyBroadException
            try:
                # noinspection PyProtectedMember
                _path = rule.matcher._path

                if re.compile(_path).match(handler.request.path):
                    return _path
            except Exception:
                pass
