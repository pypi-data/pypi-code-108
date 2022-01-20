import json

from kafka import KafkaProducer
from kafka.errors import KafkaError

from RainbowMonitoringSDK.exporters.Exporter import Exporter


class KafkaExporter(Exporter):
    """
    Kafka extractor class (TO TEST)
    """
    producer: KafkaProducer = None

    def __init__(self, brokers: str, topic: str = "metrics"):
        self.topic = topic
        self.brokers = brokers

    def run(self):  # creates the connection with Kafka
        self.producer = KafkaProducer(
            bootstrap_servers=self.brokers,
            key_serializer=str.encode,
            value_serializer=lambda m: json.dumps(m).encode('ascii')
        )

    def update(self, data: dict):
        data = Exporter.update(self, data)
        try:
            future = self.producer.send(self.topic, key=id, value=data)
            meta = future.get(timeout=10)
            return True
        except KafkaError as e:
            print(e)
        return False
