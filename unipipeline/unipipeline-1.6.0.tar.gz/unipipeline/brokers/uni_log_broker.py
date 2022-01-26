import json
import logging
from logging import Logger
from typing import Set, List, TYPE_CHECKING
from uuid import uuid4

from unipipeline.brokers.uni_broker import UniBroker, UniBrokerConsumer
from unipipeline.definitions.uni_broker_definition import UniBrokerDefinition
from unipipeline.definitions.uni_definition import UniDynamicDefinition
from unipipeline.message_meta.uni_message_meta import UniMessageMeta

if TYPE_CHECKING:
    from unipipeline.modules.uni_mediator import UniMediator


class UniLogBroker(UniBroker[UniDynamicDefinition]):
    def start_consuming(self) -> None:
        self._logger.info(f'{self._logging_prefix} start consuming')

    def get_topic_approximate_messages_count(self, topic: str) -> int:
        return 0

    def initialize(self, topics: Set[str], answer_topic: Set[str]) -> None:
        self._logger.info(f'{self._logging_prefix} initialized')

    def mk_logger(self) -> Logger:
        return logging.getLogger(__name__)

    def mk_log_prefix(self) -> str:
        return f'{type(self).__name__} {self._uni_definition.name}::{uuid4()} :'

    def __init__(self, mediator: 'UniMediator', definition: UniBrokerDefinition) -> None:
        super().__init__(mediator, definition)
        self._logger = self.mk_logger()
        self._logging_prefix = self.mk_log_prefix()

    def connect(self) -> None:
        self._logger.info(f'{self._logging_prefix} connect')

    def close(self) -> None:
        self._logger.info(f'{self._logging_prefix} close')

    def add_consumer(self, consumer: UniBrokerConsumer) -> None:
        self._logger.info(f'{self._logging_prefix} add consumer "{consumer.id}" to topic "{consumer.topic}" :: {consumer.group_id}')

    def publish(self, topic: str, meta_list: List[UniMessageMeta], alone: bool = False) -> None:
        for meta in meta_list:
            self._logger.info(f'{self._logging_prefix} publish {json.dumps(meta.dict())}')
