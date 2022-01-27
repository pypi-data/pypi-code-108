from __future__ import annotations

import json
import os

from kafka import KafkaConsumer
from .process_killer import GracefulKiller


class ConsumerWorker:
    def __init__(self, topic_name: str, kafka_hosts: str = os.getenv("KAFKA_HOSTS")):
        self.topic_name = topic_name
        self.kafka_hosts = kafka_hosts
        self.consumer = None
        self.producer = None
        self.killer = GracefulKiller()

    def poll(self) -> ConsumerWorker:
        self.consumer = KafkaConsumer(
            self.topic_name,
            bootstrap_servers=self.kafka_hosts,
            auto_offset_reset='earliest',
            group_id='main_consumer_group',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

        self.consumer.poll()

        return self

    async def listen(self, callback: callable, worker: callable) -> None:
        while not self.killer.kill_now:
            try:
                for data in self.consumer:
                    self.consumer.commit()
                    await callback(data.value, worker)
            except SystemExit:
                print(f"Shutting down")
            finally:
                self.consumer.close()

