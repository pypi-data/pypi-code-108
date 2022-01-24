"""
Instrument `kafka-python` to report instrumentation-kafka produced and consumed messages

Usage
-----

..code:: python

    from hs_sdk.src.instrumentation.kafka import KafkaInstrumentor
    from kafka import KafkaProducer, KafkaConsumer

    # Instrument kafka
    KafkaInstrumentor().instrument()

    # This will report a span of type producer with the default settings
    producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
    producer.send('my-topic', b'raw_bytes')


    # This will report a span of type consumer with the default settings
    consumer = KafkaConsumer('my-topic',
                             group_id='my-group',
                             bootstrap_servers=['localhost:9092'])
    for message in consumer:
        # process message

API
___
"""

import json
from logging import getLogger
from typing import Collection, Optional, List

from opentelemetry.context import attach
from wrapt import wrap_function_wrapper
import kafka

from opentelemetry import trace
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import Tracer, set_span_in_context
from opentelemetry.propagate import inject, extract
from opentelemetry.propagators import textmap

from helios.kafka_instrumentation.src.kafka.package import _instruments

__version__ = "0.1.0"

PRODUCER_SPAN_NAME = "kafka.send"
CONSUMER_SPAN_NAME = "kafka.consume"

SPAN_ATTRIBUTES_MESSAGING_PAYLOAD = "messaging.payload"
SPAN_ATTRIBUTES_MESSAGING_KAFKA_HEADERS = "messaging.kafka.headers"

_LOG = getLogger(__name__)


class KafkaContextGetter(textmap.Getter):
    def get(self, carrier: textmap.CarrierT, key: str) -> Optional[List[str]]:
        if carrier is None:
            return None

        for k, v in carrier:
            if k == key:
                if v is not None:
                    return [v.decode()]
        return None

    def keys(self, carrier: textmap.CarrierT) -> List[str]:
        if carrier is None:
            return []
        return [key for (key, value) in carrier]


class KafkaContextSetter(textmap.Setter):
    def set(self, carrier: textmap.CarrierT, key: str, value: str) -> None:
        if carrier is None or key is None:
            return

        if value:
            value = value.encode()
        carrier.append((key, value))


def _get_argument(key, position, default_value, args, kwargs):
    if len(args) > position:
        return args[position]
    return kwargs.get(key, default_value)


def _get_topic(args):
    """ extract topic from `send` method arguments in KafkaProducer class"""
    if len(args) > 0:
        return args[0]
    return "unknown"


def _get_value(args, kwargs):
    """ extract value from `send` method arguments in KafkaProducer class"""
    return _get_argument("value", 1, None, args, kwargs)


def _get_key(args, kwargs):
    """ extract key from `send` method arguments in KafkaProducer class"""
    return _get_argument("key", 2, None, args, kwargs)


def _get_headers(args, kwargs):
    """ extract headers from `send` method arguments in KafkaProducer class"""
    return _get_argument("headers", 3, None, args, kwargs)


def _get_partition(instance, args, kwargs):
    """ extract partition `send` method arguments, using the `_partition` method in KafkaProducer class"""
    partition = _get_argument("partition", 4, None, args, kwargs)
    topic = _get_topic(args)
    key = _get_key(args, kwargs)
    value = _get_value(args, kwargs)
    key_bytes = instance._serialize(instance.config['key_serializer'], topic, key)
    value_bytes = instance._serialize(instance.config['value_serializer'], topic, value)
    valid_types = (bytes, bytearray, memoryview, type(None))
    if type(key_bytes) not in valid_types or type(value_bytes) not in valid_types:
        return None
    try:
        return instance._partition(topic, partition, key, value, key_bytes, value_bytes)
    except Exception as err:
        _LOG.debug('Could not get partition', err)
        return None


def _create_producer_span(tracer, span_name, topic, partition, value, headers, bootstrap_servers):
    with tracer.start_as_current_span(span_name, kind=trace.SpanKind.PRODUCER) as span:
        _set_span_attributes(span, topic, partition, value, headers, bootstrap_servers)
        span.set_attribute(SpanAttributes.MESSAGING_OPERATION, 'send')
        inject(headers, context=set_span_in_context(span), setter=KafkaContextSetter())


def _create_consumer_span(tracer, span_name, topic, partition, value, headers, bootstrap_servers):
    extracted_context = extract(headers, getter=KafkaContextGetter())
    span = tracer.start_span(span_name, context=extracted_context, kind=trace.SpanKind.CONSUMER)
    new_context = trace.set_span_in_context(span, extracted_context)
    attach(new_context)
    with trace.use_span(span):
        _set_span_attributes(span, topic, partition, value, headers, bootstrap_servers)
        span.set_attribute(SpanAttributes.MESSAGING_OPERATION, 'process')


def _set_span_attributes(span, topic, partition, value, headers, bootstrap_servers):
    if span.is_recording():
        span.set_attribute(SpanAttributes.MESSAGING_SYSTEM, 'kafka')
        span.set_attribute(SpanAttributes.MESSAGING_DESTINATION, topic) if topic else None
        span.set_attribute(SPAN_ATTRIBUTES_MESSAGING_PAYLOAD, value) if value else None
        span.set_attribute(SpanAttributes.MESSAGING_KAFKA_PARTITION, partition) if partition is not None else None
        span.set_attribute(SpanAttributes.MESSAGING_URL, json.dumps(bootstrap_servers))
        span.set_attribute(SPAN_ATTRIBUTES_MESSAGING_KAFKA_HEADERS, f"{headers}")


def _instrument(tracer: Tracer):

    def _end_current_consumer_span():
        current_span = trace.get_current_span()
        if current_span.is_recording() and current_span.name == CONSUMER_SPAN_NAME:
            current_span.end()

    def _traced_send(func, instance, args, kwargs):
        span_name = PRODUCER_SPAN_NAME
        topic = _get_topic(args)
        value = _get_value(args, kwargs)
        headers = _get_headers(args, kwargs)
        if headers is None:
            headers = []
            kwargs["headers"] = headers
        partition = _get_partition(instance, args, kwargs)
        bootstrap_servers = instance.config.get('bootstrap_servers')
        _create_producer_span(tracer, span_name, topic, partition, value, headers, bootstrap_servers)
        return func(*args, **kwargs)

    def _traced_next(func, instance, args, kwargs):
        _end_current_consumer_span()
        bootstrap_servers = instance.config.get('bootstrap_servers')
        record = func(*args, **kwargs)

        if record:
            _create_consumer_span(tracer, CONSUMER_SPAN_NAME, record.topic, record.partition,
                                  record.value, record.headers, bootstrap_servers)
        return record

    def _traced_commit(func, instance, args, kwargs):
        _end_current_consumer_span()
        return func(*args, **kwargs)

    wrap_function_wrapper("kafka", "KafkaProducer.send", _traced_send)
    wrap_function_wrapper("kafka", "KafkaConsumer.__next__", _traced_next)
    wrap_function_wrapper("kafka", "KafkaConsumer.commit", _traced_commit)


class KafkaInstrumentor(BaseInstrumentor):
    """An instrumentor for kafka module
    See `BaseInstrumentor`
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs):
        """Instruments the kafka module

        Args:
            **kwargs: Optional arguments
                ``tracer_provider``: a TracerProvider, defaults to global.
        """
        tracer_provider = kwargs.get("tracer_provider")
        tracer = trace.get_tracer(
            'opentelemetry.instrumentation.kafka_python', __version__, tracer_provider=tracer_provider
        )
        _instrument(tracer)

    def _uninstrument(self, **kwargs):
        unwrap(kafka.KafkaProducer, "send")
        unwrap(kafka.KafkaConsumer, "__next__")
        unwrap(kafka.KafkaConsumer, "commit")
