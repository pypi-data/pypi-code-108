import threading

from ... import EventSource, EventSink, Event, TriggerableEventBatchSource, TriggererEventSource
from ..._private._utilities import *
from ._data_types import *
from kafka import KafkaConsumer as KC, KafkaProducer as KP


class KafkaTriggererConsumer(TriggererEventSource):
    def __init__(self,
                 topic: KafkaTopic,
                 group_id: str,
                 deserializer: Callable[[str], Any],
                 offset_reset_strategy: str = 'latest',
                 **kwargs):
        super().__init__(**kwargs)
        self.topic = topic
        self.group_id = group_id
        self.deserializer = deserializer
        self.offset_reset_strategy = offset_reset_strategy
        self.consuming: bool = False

        self.inner_consumer: KC = KC(
            self.topic.topic_id,
            bootstrap_servers=[str(self.topic.server)],
            auto_offset_reset=self.offset_reset_strategy,
            enable_auto_commit=True,
            group_id=self.group_id,
            value_deserializer=lambda x: self.deserializer(x.decode('utf-8'))
        )

    def start_generating(self) -> None:
        self.consuming = True
        threading.Thread(target=self._repetitively_generate).start()

    def _repetitively_generate(self):
        for message in self.inner_consumer:
            try:
                event = message.value
                if not isinstance(event, Event):
                    print(f'Invalid kafka message with type {str(type(event))}')  # TODO log
                else:
                    self.process_generated_event(event)
            except:
                pass  # TODO log
            finally:
                if not self.consuming:
                    break

    def stop_generating(self) -> None:
        self.consuming = False


class KafkaConsumer(TriggerableEventBatchSource):
    def __init__(self,
                 topic: KafkaTopic,
                 group_id: str,
                 deserializer: Callable[[str], Any],
                 offset_reset_strategy: str = 'latest',
                 max_records: int = None,
                 timeout_ms: int = 6000,
                 **kwargs):
        super().__init__(**kwargs)
        self.topic = topic
        self.group_id = group_id
        self.deserializer = deserializer
        self.offset_reset_strategy = offset_reset_strategy
        self.max_records = max_records
        self.timeout_ms: int = timeout_ms
        self.inner_consumer: KC = KC(
            self.topic.topic_id,
            bootstrap_servers=[str(self.topic.server)],
            auto_offset_reset=self.offset_reset_strategy,
            enable_auto_commit=True,
            group_id=self.group_id,
            value_deserializer=lambda x: self.deserializer(x.decode('utf-8'))
        )

    def get_event_batch(self) -> List[Event]:
        records: Dict = \
            self.inner_consumer.poll(timeout_ms=self.timeout_ms, max_records=self.max_records) \
                if self.max_records is not None \
                else self.inner_consumer.poll(timeout_ms=self.timeout_ms)
        record_list: List[Event] = []
        for tp, consumer_records in records.items():
            for consumer_record in consumer_records:
                event = consumer_record.value
                if not isinstance(event, Event):
                    print(f'Invalid kafka message with type {str(type(event))}')  # TODO log
                else:
                    record_list.append(event)
        return record_list


class KafkaProducer(EventSink):
    def __init__(self,
                 topic: KafkaTopic,
                 serializer: Callable[[Any], str],
                 **kwargs):
        super().__init__(**kwargs)
        self.topic = topic
        self.serializer = serializer

        self.inner_producer: KP = KP(bootstrap_servers=[str(self.topic.server)],
                                     value_serializer=lambda x: self.serializer(x).encode('utf-8'))

    def drown_event(self, event: Event) -> None:
        self.inner_producer.send(self.topic.topic_id, value=event)
