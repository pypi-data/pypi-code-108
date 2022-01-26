from typing import Dict, List, Tuple
import wrapt
from opentelemetry.semconv.trace import SpanAttributes

from opentelemetry.trace import Span

from helios.instrumentation.base_http_instrumentor import HeliosBaseHttpInstrumentor


class HeliosFlaskInstrumentor(HeliosBaseHttpInstrumentor):
    MODULE_NAME = 'opentelemetry.instrumentation.flask'
    INSTRUMENTOR_NAME = 'FlaskInstrumentor'
    RESPONSE_BODY_HEADER_NAME = 'HS-Response-body'
    FLASK_REQUEST_VAR_NAME = 'werkzeug.request'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)
        self.tracer_provider = None
        self.instrumented_apps = set()

    def instrument(self, tracer_provider=None):
        if self.get_instrumentor() is None:
            return

        self.tracer_provider = tracer_provider
        wrapt.wrap_function_wrapper('flask', 'Flask.__init__', self.flask_instrument_and_run)

    def uninstrument(self):
        if self.get_instrumentor() is None:
            return

        for app in self.instrumented_apps:
            self.get_instrumentor().uninstrument_app(app)
        self.instrumented_apps = set()

    def flask_instrument_and_run(self, wrapped, instance, args, kwargs):
        res = wrapped(*args, **kwargs)
        if instance not in self.instrumented_apps:
            self.instrumented_apps.add(instance)
            instance.after_request(self.flask_response_callback)
            self.get_instrumentor().instrument_app(instance,
                                                   tracer_provider=self.tracer_provider,
                                                   request_hook=self.request_hook,
                                                   response_hook=self.response_hook)
        return res

    @staticmethod
    def request_hook(span: Span, flask_request_environ: Dict) -> None:
        try:
            if span is None:
                return

            # Extracting request body
            request = flask_request_environ.get(HeliosFlaskInstrumentor.FLASK_REQUEST_VAR_NAME)
            if request:
                url = request.url
                body = request.data
                body = request.json if body is None else body
            else:
                body = None
                url = None
        except Exception:
            pass

        span.set_attribute(SpanAttributes.HTTP_URL, url) if url else None

        HeliosFlaskInstrumentor.base_request_hook(span, dict(request.headers), body)

    @staticmethod
    def response_hook(span: Span, status: str, response_headers: List[Tuple[str]]) -> None:
        if span is None:
            return

        body = None
        headers = dict()

        for header in response_headers:
            if len(header) != 2:
                continue
            key, value = header
            if key == HeliosFlaskInstrumentor.RESPONSE_BODY_HEADER_NAME:
                body = value
                response_headers.remove(header)
            else:
                headers[key] = value

        HeliosFlaskInstrumentor.base_response_hook(span, headers, body)

    @staticmethod
    def flask_response_callback(response):
        try:
            if response is None:
                return None
            body = response.data
            body = response.json if body is None else body
            if body is None:
                return response
            if type(body) == bytes:
                body = body.decode()
            body = body.replace("\n", " ")
            response.headers.add(HeliosFlaskInstrumentor.RESPONSE_BODY_HEADER_NAME, body)
        except Exception:
            pass

        return response
