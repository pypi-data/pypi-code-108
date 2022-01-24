import json
from opentelemetry.trace import Span
from typing import List, Optional, Tuple
from urllib.parse import parse_qsl

from helios.instrumentation.base_http_instrumentor import HeliosBaseHttpInstrumentor


class HeliosHttpxInstrumentor(HeliosBaseHttpInstrumentor):
    MODULE_NAME = 'helios.httpx_instrumentation.src.httpx'
    INSTRUMENTOR_NAME = 'HTTPXClientInstrumentor'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None):
        if self.get_instrumentor() is None:
            return

        self.get_instrumentor().instrument(tracer_provider=tracer_provider,
                                           request_hook=self.request_hook,
                                           response_hook=self.response_hook)

    def request_hook(self, span: Span, request):
        if request.stream is None:
            payload = None
        else:
            payload = json.dumps(dict(parse_qsl(request.stream.read().decode('utf-8'))))

        HeliosBaseHttpInstrumentor.base_request_hook(span, self.parse_headers(request.headers), payload)

    def response_hook(self, span: Span, _request, response):
        payload = None

        # TODO: Do not extract the response body, as it drains the data and makes it inaccessible later.
        # for member in response.stream:
        #     if payload is None:
        #         payload = member.decode('utf-8')
        #     else:
        #         payload += member.decode('utf-8')

        HeliosBaseHttpInstrumentor.base_response_hook(span, self.parse_headers(response.headers), payload)

    @staticmethod
    def parse_headers(headers: Optional[List[Tuple[bytes, bytes]]]):
        if headers is None:
            return None
        else:
            return {
                key.decode('utf-8') if type(key) == bytes
                else key: value.decode('utf-8') if type(value) == bytes
                else value for key, value in dict(headers).items()
            }
