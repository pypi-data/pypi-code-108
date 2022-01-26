import json

from opentelemetry.trace import Span
from opentelemetry.semconv.trace import SpanAttributes

from helios.instrumentation.base import HeliosBaseInstrumentor


class HeliosElasticsearchInstrumentor(HeliosBaseInstrumentor):

    MODULE_NAME = 'opentelemetry.instrumentation.elasticsearch'
    INSTRUMENTOR_NAME = 'ElasticsearchInstrumentor'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None):
        if self.get_instrumentor() is None:
            return

        self.get_instrumentor().instrument(tracer_provider=tracer_provider, request_hook=self.request_hook, response_hook=self.response_hook)

    def request_hook(self, span: Span, method, url, kwargs):
        if span and span.is_recording():
            span.set_attribute(SpanAttributes.DB_NAME, 'Elasticsearch')

    def response_hook(self, span: Span, response):
        if response is None:
            return
        if span and span.is_recording():
            response_str = json.dumps(response)
            if len(response_str) <= self.MAX_PAYLOAD_SIZE:
                span.set_attribute(self.DB_QUERY_RESULT_ATTRIBUTE_NAME, response_str)
