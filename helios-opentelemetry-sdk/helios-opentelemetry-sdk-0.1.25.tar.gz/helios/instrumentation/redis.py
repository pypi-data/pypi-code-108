import json

from opentelemetry.trace import Span

from helios.instrumentation.base import HeliosBaseInstrumentor


class HeliosRedisInstrumentor(HeliosBaseInstrumentor):
    MODULE_NAME = 'opentelemetry.instrumentation.redis'
    INSTRUMENTOR_NAME = 'RedisInstrumentor'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None):
        if self.get_instrumentor() is None:
            return

        self.get_instrumentor().instrument(tracer_provider=tracer_provider, response_hook=self.response_hook)

    def response_hook(self, span: Span, connection, response):
        if not span or not span.is_recording():
            return

        try:
            query_result = None
            response_type = type(response)
            if response_type in [str, int, bool, float]:
                query_result = response
            elif response_type == bytes:
                query_result = response.decode()
            elif response_type in [tuple, dict, list]:
                query_result = json.dumps(response)

            if not hasattr(query_result, '__len__') or len(query_result) <= self.MAX_PAYLOAD_SIZE:
                span.set_attribute(self.DB_QUERY_RESULT_ATTRIBUTE_NAME, query_result)
        except Exception:
            pass
