from typing import Dict, TypeVar, Set, List, TYPE_CHECKING
from uuid import UUID

from unipipeline.brokers.uni_broker import UniBroker
from unipipeline.brokers.uni_broker_consumer import UniBrokerConsumer
from unipipeline.definitions.uni_broker_definition import UniBrokerDefinition
from unipipeline.brokers.uni_memory_broker_queue import UniMemoryBrokerQueue
from unipipeline.definitions.uni_definition import UniDynamicDefinition
from unipipeline.message_meta.uni_message_meta import UniMessageMeta, UniAnswerParams

if TYPE_CHECKING:
    from unipipeline.modules.uni_mediator import UniMediator


TItem = TypeVar('TItem')


class UniMemoryBroker(UniBroker[UniDynamicDefinition]):

    def stop_consuming(self) -> None:
        pass

    def __init__(self, mediator: 'UniMediator', definition: UniBrokerDefinition) -> None:
        super(UniMemoryBroker, self).__init__(mediator, definition)
        self._consuming_started = False
        self._queues_by_topic: Dict[str, UniMemoryBrokerQueue] = dict()
        self._consumers_count = 0

    def get_topic_approximate_messages_count(self, topic: str) -> int:
        return self._queues_by_topic[topic].messages_to_process_count()

    def initialize(self, topics: Set[str], answer_topic: Set[str]) -> None:
        for topic in topics:
            self._init_queue(topic)

    def _init_queue(self, topic: str) -> None:
        if topic in self._queues_by_topic:
            return
        self._queues_by_topic[topic] = UniMemoryBrokerQueue(self.echo.mk_child(f'topic[{topic}]'))

    def _get_answer_topic_name(self, topic: str, answ_id: UUID) -> str:
        return f'answer@{topic}@{answ_id}'

    def connect(self) -> None:
        pass

    def close(self) -> None:
        pass

    def add_consumer(self, consumer: UniBrokerConsumer) -> None:
        self._consumers_count += 1
        self._queues_by_topic[consumer.topic].add_listener(consumer.message_handler, 1)
        self.echo.log_info(f'consumer for topic "{consumer.topic}" added with consumer_tag "{consumer.id}"')

    def start_consuming(self) -> None:
        if self._consuming_started:
            raise OverflowError('consuming has already started')

        if self._consumers_count == 0:
            self.echo.log_warning('has no consumers')
            return

        self._consuming_started = True

        self.echo.log_info('start consuming')
        for ql in self._queues_by_topic.values():
            ql.process_all()

    def publish(self, topic: str, meta_list: List[UniMessageMeta], alone: bool = False) -> None:
        ql = self._queues_by_topic[topic]
        for meta in meta_list:
            ql.add(meta)
        if self._consuming_started:
            ql.process_all()

    def get_answer(self, answer_params: UniAnswerParams, max_delay_s: int, unwrapped: bool) -> UniMessageMeta:
        topic = self._get_answer_topic_name(answer_params.topic, answer_params.id)
        self._init_queue(topic)

        answ_meta = self._queues_by_topic[topic].get_next()

        if unwrapped:
            return UniMessageMeta.create_new(answ_meta.payload, unwrapped=True)

        return answ_meta

    def publish_answer(self, answer_params: UniAnswerParams, meta: UniMessageMeta) -> None:
        topic = self._get_answer_topic_name(answer_params.topic, answer_params.id)
        self._init_queue(topic)
        self._queues_by_topic[topic].add(meta)
