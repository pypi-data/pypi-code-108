import json
from logging import getLogger
from unittest import TestCase

from kafka import KafkaConsumer, KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import SpanKind

from helios.kafka_instrumentation.src.kafka import KafkaInstrumentor
from helios.kafka_instrumentation.src.kafka import SPAN_ATTRIBUTES_MESSAGING_KAFKA_HEADERS, SPAN_ATTRIBUTES_MESSAGING_PAYLOAD

_LOG = getLogger(__name__)


class TestKafka(TestCase):
    """
    For running these tests we need to have a kafka server running locally (see `self.bootstrap_servers`)
     with a topic named as defined in `self.topic` with 2 partitions
    """

    def setUp(self) -> None:
        self.span_exporter = InMemorySpanExporter()
        self.span_processor = BatchSpanProcessor(self.span_exporter)
        self.tracer_provider = TracerProvider()
        self.tracer_provider.add_span_processor(self.span_processor)

        self.tracer_provider.force_flush()
        self.span_exporter.clear()

        KafkaInstrumentor().instrument(tracer_provider=self.tracer_provider)

        self.topic = "test"
        self.bootstrap_servers = ['localhost:9093']
        self.admin = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers, client_id="admin")

        if self.topic in self.admin.list_topics():
            self.admin.delete_topics([self.topic])
        self.admin.create_topics(new_topics=[NewTopic(name=self.topic, num_partitions=2, replication_factor=1)])

    def tearDown(self) -> None:
        self.admin.delete_topics([self.topic])
        self.tracer_provider.force_flush()
        self.span_exporter.clear()
        KafkaInstrumentor().uninstrument()

    def _consume(self, consumer: KafkaConsumer):
        record = next(consumer)
        consumer.commit()
        return record

    def test_span_properties(self):
        test_headers = [("header_key", b"header_value")]
        message = b'this is a test message'

        try:
            producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers)
            consumer = KafkaConsumer(self.topic, group_id='my-group', bootstrap_servers=self.bootstrap_servers,
                                     auto_offset_reset='earliest')
        except Exception:
            self.fail(f"No bootstrap servers were found on {self.bootstrap_servers}. please run a kafka container")

        producer.send(self.topic, value=message, partition=0, headers=test_headers[:])
        producer.send(self.topic, message, b"key", test_headers[:], 1)

        self._consume(consumer)
        self._consume(consumer)

        producer.close()
        consumer.close()
        self.tracer_provider.force_flush()

        spans = self.span_exporter.get_finished_spans()
        self.assertEqual(4, len(spans))
        producer_partition_0, producer_partition_1 = False, False
        consumer_partition_0, consumer_partition_1 = False, False

        for span in spans:
            attributes = span.attributes
            span_topic = attributes.get(SpanAttributes.MESSAGING_DESTINATION)
            span_url = attributes.get(SpanAttributes.MESSAGING_URL)
            span_system = attributes.get(SpanAttributes.MESSAGING_SYSTEM)
            span_operation = attributes.get(SpanAttributes.MESSAGING_OPERATION)
            span_headers = attributes.get(SPAN_ATTRIBUTES_MESSAGING_KAFKA_HEADERS)
            span_partition = attributes.get(SpanAttributes.MESSAGING_KAFKA_PARTITION)
            span_payload = attributes.get(SPAN_ATTRIBUTES_MESSAGING_PAYLOAD)

            self.assert_common_attributes(span_system, span_topic, span_url, span_payload, message)
            if span.kind == SpanKind.PRODUCER:
                self.assert_producer_attributes(span_operation, span_headers, test_headers)
                if span_partition == 0:
                    producer_partition_0 = True
                elif span_partition == 1:
                    producer_partition_1 = True
                else:
                    self.fail(f"partition should be either 0 or 1, but got: {span_partition}")

            elif span.kind == SpanKind.CONSUMER:
                self.assert_consumer_attributes(span_operation, span_headers)
                if span_partition == 0:
                    consumer_partition_0 = True
                elif span_partition == 1:
                    consumer_partition_1 = True
                else:
                    self.fail(f"partition should be either 0 or 1, but got: {span_partition}")

        self.assertTrue(consumer_partition_0 and consumer_partition_1)
        self.assertTrue(producer_partition_0 and producer_partition_1)

    def test_instrument_uninstrument(self):
        message = b'this is a test message'
        KafkaInstrumentor().uninstrument()

        # Test Instrument
        KafkaInstrumentor().instrument(tracer_provider=self.tracer_provider)

        try:
            producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers)
            consumer = KafkaConsumer(self.topic, group_id='my-group', bootstrap_servers=self.bootstrap_servers,
                                     auto_offset_reset='earliest')
        except Exception:
            self.fail(f"No bootstrap servers were found on {self.bootstrap_servers}. please run a kafka container")

        producer.send(self.topic, message)
        self._consume(consumer)

        self.tracer_provider.force_flush()

        spans = self.span_exporter.get_finished_spans()
        self.assertEqual(2, len(spans))
        self.span_exporter.clear()

        # Test Uninstrument
        KafkaInstrumentor().uninstrument()

        producer.send(self.topic, message)
        self._consume(consumer)

        producer.close()
        consumer.close()
        self.tracer_provider.force_flush()

        spans = self.span_exporter.get_finished_spans()
        self.assertEqual(0, len(spans))

    def test_context_propagation(self):
        try:
            producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers)
            consumer = KafkaConsumer(self.topic, group_id='my-group', bootstrap_servers=self.bootstrap_servers,
                                     auto_offset_reset='earliest')
        except Exception:
            self.fail(f"No bootstrap servers were found on {self.bootstrap_servers}. please run a kafka container")

        producer.send(self.topic, b'this is a test message', headers=[])
        self._consume(consumer)

        producer.close()
        consumer.close()
        self.tracer_provider.force_flush()

        spans = self.span_exporter.get_finished_spans()
        self.assertEqual(2, len(spans))

        producer_span = spans[0]
        consumer_span = spans[1]

        self.assertEqual(producer_span.context.trace_id, consumer_span.context.trace_id)
        self.assertEqual(producer_span.context.span_id, consumer_span.parent.span_id)

    def assert_producer_attributes(self, span_operation, span_headers, expected_headers):
        self.assertEqual('send', span_operation)
        self.assertEqual(f"{expected_headers}", span_headers)

    def assert_consumer_attributes(self, span_operation, span_headers):
        self.assertEqual('process', span_operation)
        self.assertNotEqual("", span_headers)
        self.assertIsNotNone(span_headers)

    def assert_common_attributes(self, span_system, span_topic, span_url, span_payload, expected_payload):
        self.assertEqual('kafka', span_system)
        self.assertEqual(self.topic, span_topic)
        self.assertEqual(json.dumps(self.bootstrap_servers), span_url)
        self.assertEqual(expected_payload.decode(), span_payload)
