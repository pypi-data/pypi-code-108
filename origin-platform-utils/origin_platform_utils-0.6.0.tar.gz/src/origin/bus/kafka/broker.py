from typing import List, Any, Iterable, Dict
from functools import cached_property
from kafka import KafkaProducer, KafkaConsumer

from origin.bus.serialize import MessageSerializer
from origin.bus.broker import MessageBroker, Message, TTopicList


class KafkaMessageBroker(MessageBroker):
    """
    Implementation of Kafka as message bus.
    """
    def __init__(
            self,
            group: str,
            servers: List[str],
            serializer: MessageSerializer,
    ):
        self.group = group
        self.servers = servers
        self.serializer = serializer

    @cached_property
    def _kafka_producer(self) -> KafkaProducer:
        """
        TODO
        """
        return KafkaProducer(
            bootstrap_servers=self.servers,
            value_serializer=self.serializer.serialize,

        )

    @cached_property
    def _kafka_consumer(self) -> KafkaConsumer:
        """
        TODO
        """

        return KafkaConsumer(
            bootstrap_servers=self.servers,
            value_deserializer=self.serializer.deserialize,
            group_id=self.group,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
        )

    def __iter__(self) -> Iterable[Message]:
        """
        Returns an iterable of messages received in any
        of the subscribed topics.
        """
        return (msg.value for msg in self._kafka_consumer)

    def poll(self, timeout: int = 0) -> Dict[str, List[Message]]:
        """
        Polls the broker for at least one message with a timeout.
        Returns messages mapped by topic.

        :param timeout: Timeout in seconds
        """
        res = self._kafka_consumer.poll(timeout_ms=timeout * 1000)

        return {
            partition.topic: [record.value for record in record_list]
            for partition, record_list in res.items()
        }

    def poll_list(self, timeout: int = 0) -> List[Message]:
        """
        Polls the broker for at least one message with a timeout.
        Returns a list of messages from any topics subscribed to.

        :param timeout: Timeout in seconds
        """
        res = self._kafka_consumer.poll(timeout_ms=timeout * 1000)

        return [
            record.value
            for record_list in res.values()
            for record in record_list
        ]

    def subscribe(self, topics: TTopicList):
        """
        Subscribe to a number of topics.

        :param topics: The topics to subscribe to
        """
        self._kafka_consumer.subscribe(topics)

    def publish(self, topic: str, msg: Any, block=True, timeout=10):
        """
        TODO
        """
        print('PUBLISH: %s' % msg)
        self._kafka_producer.send(topic=topic, value=msg)
        self._kafka_producer.flush()

        # future = self._kafka_producer.send(
        #     topic=topic,
        #     value=msg,
        # )
        #
        # if block:
        #     try:
        #         record_metadata = future.get(timeout=timeout)
        #     except KafkaError as e:
        #         # Decide what to do if produce request failed...
        #         raise self.PublishError(str(e))
