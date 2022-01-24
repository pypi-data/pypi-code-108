import json
from logging import getLogger
from helios.instrumentation.base import HeliosBaseInstrumentor
from opentelemetry.trace import Span
from opentelemetry.semconv.trace import SpanAttributes

_LOG = getLogger(__name__)


class PikaSpanAttributes:
    MESSAGING_PAYLOAD = 'messaging.payload'
    RABBIT_MQ_HEADERS = 'rabbitmq.headers'
    SEND_NAME = 'rabbitmq.sendMessage'
    RECEIVE_NAME = 'rabbitmq.receiveMessage'


class HeliosPikaInstrumentor(HeliosBaseInstrumentor):
    MODULE_NAME = 'helios.pika_instrumentation'
    INSTRUMENTOR_NAME = 'PikaInstrumentor'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None):
        if self.get_instrumentor() is None:
            return

        self.get_instrumentor().instrument(tracer_provider=tracer_provider, publish_hook=self.publish_hook,
                                           consume_hook=self.consume_hook)

    def publish_hook(self, span: Span, body: bytes, properties: dict):
        span.update_name(PikaSpanAttributes.SEND_NAME)
        self.set_common_attributes(span, body, properties)
        span.set_attribute('span.operation', PikaSpanAttributes.SEND_NAME)

    def consume_hook(self, span: Span, body: bytes, properties):
        span.update_name(PikaSpanAttributes.RECEIVE_NAME)
        self.set_common_attributes(span, body, properties)
        span.set_attribute('span.operation', PikaSpanAttributes.RECEIVE_NAME)

    def set_common_attributes(self, span: Span, body: bytes, properties):
        string_body = None
        if type(body) == str:
            string_body = body
        elif type(body) == bytes:
            string_body = body.decode()
        else:
            _LOG.debug('Cannot parse body')
        span.set_attribute(PikaSpanAttributes.MESSAGING_PAYLOAD, string_body) if string_body else None
        span.set_attribute(PikaSpanAttributes.RABBIT_MQ_HEADERS, json.dumps(properties.headers))
        messaging_url = span.attributes.get(SpanAttributes.NET_PEER_NAME, None)
        span.set_attribute(SpanAttributes.MESSAGING_URL, messaging_url) if messaging_url else None
        routing_key = span.attributes['span.operation'].split()[0]
        span.set_attribute(SpanAttributes.MESSAGING_RABBITMQ_ROUTING_KEY, routing_key) if routing_key else None
        span.set_attribute(SpanAttributes.MESSAGING_DESTINATION, 'amq.topic')
        span.set_attribute(SpanAttributes.MESSAGING_DESTINATION_KIND, 'topic')
        span.set_attribute(SpanAttributes.MESSAGING_PROTOCOL, 'amqp')
