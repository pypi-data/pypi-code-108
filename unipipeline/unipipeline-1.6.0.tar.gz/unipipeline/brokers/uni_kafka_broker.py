from typing import Optional, Any, Dict, List, Set, TYPE_CHECKING

from kafka import KafkaProducer, KafkaConsumer  # type: ignore

from unipipeline.brokers.uni_broker import UniBroker
from unipipeline.brokers.uni_broker_consumer import UniBrokerConsumer
from unipipeline.definitions.uni_broker_definition import UniBrokerDefinition
from unipipeline.brokers.uni_kafka_broker_config import UniKafkaBrokerConfig
from unipipeline.brokers.uni_kafka_broker_message_manager import UniKafkaBrokerMessageManager
from unipipeline.message_meta.uni_message_meta import UniMessageMeta

if TYPE_CHECKING:
    from unipipeline.modules.uni_mediator import UniMediator


class UniKafkaBroker(UniBroker[UniKafkaBrokerConfig]):
    config_type = UniKafkaBrokerConfig

    def get_boostrap_servers(self) -> List[str]:
        raise NotImplementedError(f'method get_boostrap_server must be implemented for {type(self).__name__}')

    def get_security_conf(self) -> Dict[str, Any]:
        raise NotImplementedError(f'method get_security_conf must be implemented for {type(self).__name__}')

    def __init__(self, mediator: 'UniMediator', definition: UniBrokerDefinition) -> None:
        super().__init__(mediator, definition)

        self._bootstrap_servers = self.get_boostrap_servers()

        self._producer: Optional[KafkaProducer] = None

        self._security_conf: Dict[str, Any] = self.get_security_conf()

        self._consumers: List[UniBrokerConsumer] = list()
        self._kfk_active_consumers: List[KafkaConsumer] = list()

        self._consuming_started = False
        self._interrupted = False
        self._in_processing = False

    def stop_consuming(self) -> None:    # TODO
        self._end_consuming()

    def _end_consuming(self) -> None:
        if not self._consuming_started:
            return
        self._interrupted = True
        if not self._in_processing:
            for kfk_consumer in self._kfk_active_consumers:
                kfk_consumer.close()
            self._consuming_started = False
            self.echo.log_info('consumption stopped')

    def get_topic_approximate_messages_count(self, topic: str) -> int:
        return 0  # TODO

    def initialize(self, topics: Set[str], answer_topic: Set[str]) -> None:
        pass  # TODO

    def connect(self) -> None:
        if self._producer is not None:
            if self._producer._closed:
                self._producer.close()
                self._producer = None
            else:
                return

        # TODO: change default connection as producer yo abstract connection to kafka server
        self._producer = KafkaProducer(
            bootstrap_servers=self._bootstrap_servers,
            api_version=self.config.api_version,
            retries=self.config.retry_max_count,
            acks=1,
            **self._security_conf,
        )

        if not self._producer.bootstrap_connected():
            raise ConnectionError()

        self.echo.log_info('connected')

    def close(self) -> None:
        if self._producer is not None:
            self._producer.close()
            self._producer = None
        for kfk_consumer in self._kfk_active_consumers:
            kfk_consumer.close()

    def add_consumer(self, consumer: UniBrokerConsumer) -> None:
        self._consumers.append(consumer)

    def start_consuming(self) -> None:
        echo = self.echo.mk_child('consuming')
        if len(self._consumers) == 0:
            echo.log_warning('has no consumers to start consuming')
            return
        if self._consuming_started:
            echo.log_warning('consuming has already started. ignored')
            return
        self._consuming_started = True
        self._interrupted = False
        self._in_processing = False

        if len(self._consumers) != 1:
            raise OverflowError('invalid consumers number. this type of brokers not supports multiple consumers')

        consumer = self._consumers[0]
        kfk_consumer = KafkaConsumer(
            consumer.topic,
            api_version=self.config.api_version,
            bootstrap_servers=self._bootstrap_servers,
            enable_auto_commit=False,
            group_id=consumer.group_id,
        )

        self._kfk_active_consumers.append(kfk_consumer)

        def commit() -> None:
            kfk_consumer.commit()

        # TODO: retry
        for consumer_record in kfk_consumer:
            self._in_processing = True

            meta = self.parse_message_body(consumer_record.value, self.definition.compression, self.definition.content_type, consumer.unwrapped)

            manager = UniKafkaBrokerMessageManager(commit)
            consumer.message_handler(meta, manager)

            self._in_processing = False
            if self._interrupted:
                self._end_consuming()
                break

        for kfk_consumer in self._kfk_active_consumers:
            kfk_consumer.close()

    def _get_producer(self) -> KafkaProducer:
        self.connect()
        assert self._producer is not None
        return self._producer

    def publish(self, topic: str, meta_list: List[UniMessageMeta], alone: bool = False) -> None:
        # TODO: alone
        # TODO: ttl
        # TODO: retry
        self.echo.log_debug(f'publishing the messages: {meta_list}')

        p = self._get_producer()

        for meta in meta_list:
            p.send(
                topic=topic,
                value=self.serialize_message_body(meta),
                key=str(meta.id).encode('utf8')
            )
        p.flush()
