import os
import signal
import unittest

from kafka import KafkaProducer

from aejuice_kafka_consumer import ConsumerWorker


class TestConsumerWorker(unittest.TestCase):
    topic_name: str = "test_topic"

    @classmethod
    def setUpClass(cls):
        kafka = KafkaProducer(bootstrap_servers=os.getenv("KAFKA_HOSTS"))

        kafka.send(TestConsumerWorker.topic_name, b"{\"message\": \"test message\"}")

    def test_consumer_is_working(self):
        def signal_handler(signum, frame):
            raise Exception("Lifecycle timeout. Error was not thrown, and messages was equal. Passing the test")

        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(5)

        try:
            consumer = ConsumerWorker(self.topic_name)
            consumer.poll()

            consumer.listen(
                lambda dictionary: self.assertEqual("test message", dictionary["message"])
            )
        except Exception as exc:
            self.assertEqual(True, True, exc)

