import importlib
from logging import getLogger

from opentelemetry.trace import Span
from opentelemetry.semconv.trace import SpanAttributes

from helios.instrumentation.base_http_instrumentor import HeliosBaseHttpInstrumentor

_LOG = getLogger(__name__)


class HeliosDjangoInstrumentor(HeliosBaseHttpInstrumentor):

    MODULE_NAME = 'opentelemetry.instrumentation.django'
    INSTRUMENTOR_NAME = 'DjangoInstrumentor'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)
        if self.get_instrumentor() is not None:
            try:
                django_mod = importlib.import_module('django.conf')
                django_settings = getattr(django_mod, 'settings', None)
                if django_settings is not None:
                    django_settings.configure()
            except Exception as err:
                _LOG.warning(err)

    def instrument(self, tracer_provider=None):
        if self.get_instrumentor() is None:
            return

        self.get_instrumentor().instrument(tracer_provider=tracer_provider, response_hook=self.response_hook)

    @staticmethod
    def extract_old_request_http_headers(request):
        if request.META is None or request.META.items() is None:
            return {}
        return dict((h.replace('HTTP_', ''), v) for (h, v) in request.META.items() if h.startswith('HTTP_'))

    @staticmethod
    def extract_old_response_http_headers(response):
        if getattr(response, '_headers', None) is None:
            return {}
        return dict((k, v[1]) for (k, v) in response._headers.items())

    @staticmethod
    def extract_route(request):
        match = getattr(request, "resolver_match", None)
        if match is None or getattr(match, 'kwargs') is None:
            return None

        path = request.path
        split_path = path.split('/')
        for key, value in match.kwargs.items():
            value = str(value)
            count = split_path.count(value)
            if count != 1:
                # We either populate all placeholders or none of them
                return None

            index = split_path.index(value)
            split_path[index] = f':{key}'

        return '/'.join(split_path)

    @staticmethod
    def extract_request_body(request):
        # django reads request 'body' from stream once and stores it into '_body' for further calls
        # to protect for any race condition resulting in trying to read from an already-consumed stream,
        # we attempt to directly read from '_body' first (after checking for the '_read_started' flag,
        # which is a pre-requisite for '_body' to hold content).
        # If we don't find any data, we call 'body' to invoke the stream, and if this also fails, we just return None.
        try:
            if getattr(request, '_read_started', False):
                return getattr(request, '_body', None)
            return getattr(request, 'body', None)
        except Exception:
            _LOG.warning('failed extracting request body')
            return None

    @staticmethod
    def response_hook(span: Span, request, response) -> None:
        """
        :param span: an object of type
        :param request: an object of type requests.HttpRequest
        :param response: an object of type requests.HttpResponse
        """
        route = span.attributes.get(SpanAttributes.HTTP_ROUTE, None)
        if route is None:
            route = HeliosDjangoInstrumentor.extract_route(request)
            span.set_attribute(SpanAttributes.HTTP_ROUTE, route) if route else None
        if route is None:
            url = span.attributes.get(SpanAttributes.HTTP_URL)
            span.set_attribute(SpanAttributes.HTTP_ROUTE, url) if url else None

        # older WSGI request/response objects have no 'headers' attribute
        req_headers = getattr(request, "headers", HeliosDjangoInstrumentor.extract_old_request_http_headers(request))
        res_headers = getattr(response, "headers", HeliosDjangoInstrumentor.extract_old_response_http_headers(response))

        request_body = HeliosDjangoInstrumentor.extract_request_body(request)

        HeliosDjangoInstrumentor.base_request_hook(span, req_headers, request_body)
        HeliosDjangoInstrumentor.base_response_hook(span, res_headers, response.content)
