from time import sleep, time
from typing import Dict, TypeVar, Any, Set, Union, Optional, Type, List, NamedTuple, Callable
from uuid import uuid4

from unipipeline.errors.uni_payload_error import UniPayloadSerializationError
from unipipeline.errors.uni_work_flow_error import UniWorkFlowError
from unipipeline.answer.uni_answer_message import UniAnswerMessage
from unipipeline.brokers.uni_broker import UniBroker, UniBrokerConsumer
from unipipeline.config.uni_config import UniConfig
from unipipeline.modules.uni_cron_job import UniCronJob
from unipipeline.utils.uni_echo import UniEcho
from unipipeline.message.uni_message import UniMessage
from unipipeline.message_meta.uni_message_meta import UniMessageMeta, UniMessageMetaErrTopic, UniAnswerParams
from unipipeline.utils.uni_util import UniUtil
from unipipeline.worker.uni_worker import UniWorker
from unipipeline.worker.uni_worker_consumer import UniWorkerConsumer
from unipipeline.definitions.uni_worker_definition import UniWorkerDefinition
from unipipeline.utils.sig import soft_interruption

TWorker = TypeVar('TWorker', bound=UniWorker[Any, Any])


class UniBrokerInitRecipe(NamedTuple):
    topics: Set[str]
    answer_topics: Set[str]


class UniMediator:
    def __init__(self, util: UniUtil, echo: UniEcho, config: UniConfig) -> None:
        self._config = config
        self._echo = echo
        self._util = util

        self._worker_definition_by_type: Dict[Any, UniWorkerDefinition] = dict()
        self._worker_instance_indexes: Dict[str, UniWorkerConsumer[Any, Any]] = dict()
        self._broker_instance_indexes: Dict[str, UniBroker[Any]] = dict()
        self._worker_init_list: Set[str] = set()
        self._worker_initialized_list: Set[str] = set()
        self._waiting_init_list: Set[str] = set()
        self._waiting_initialized_list: Set[str] = set()

        self._consumers_list: Set[str] = set()
        self._brokers_with_topics_to_init: Dict[str, UniBrokerInitRecipe] = dict()
        self._brokers_with_topics_initialized: Dict[str, UniBrokerInitRecipe] = dict()

        self._message_types: Dict[str, Type[UniMessage]] = dict()

        self._connected_brokers: List[UniBroker[Any]] = list()
        self._brokers_with_active_consumption: List[UniBroker[Any]] = list()

        self._decompression_modules: Dict[str, Callable[[bytes], bytes]] = dict()
        self._compression_modules: Dict[str, Callable[[bytes], bytes]] = dict()
        self._content_type_serializers: Dict[str, Callable[[Dict[str, Any]], Union[str, bytes]]] = dict()
        self._content_type_parsers: Dict[str, Callable[[Union[str, bytes]], Dict[str, Any]]] = dict()

    @property
    def echo(self) -> UniEcho:
        return self._echo

    def set_echo_level(self, level: int) -> None:
        self.echo.level = level

    def get_broker(self, name: str, singleton: bool = True) -> UniBroker[Any]:
        if not singleton:
            broker_def = self.config.brokers[name]
            broker_type = broker_def.type.import_class(UniBroker, self.echo, util=self._util)
            br = broker_type(mediator=self, definition=broker_def)
            return br
        if name not in self._broker_instance_indexes:
            self._broker_instance_indexes[name] = self.get_broker(name, singleton=False)
        return self._broker_instance_indexes[name]

    def move_to_error_topic(self, wd: UniWorkerDefinition, meta: UniMessageMeta, err_topic: UniMessageMetaErrTopic, err: Exception) -> None:
        self._echo.log_error(str(err))
        meta = meta.create_error_child(err_topic, err)
        br = self.get_broker(wd.broker.name)
        error_topic = wd.error_topic
        if error_topic == UniMessageMetaErrTopic.MESSAGE_PAYLOAD_ERR.value:
            error_topic = wd.error_payload_topic
        br.publish(error_topic, [meta])

    def add_worker_to_consume_list(self, name: str) -> None:
        wd = self._config.workers[name]
        if wd.marked_as_external:
            raise OverflowError(f'your could not use worker "{name}" as consumer. it marked as external "{wd.external}"')
        self._consumers_list.add(name)
        self.echo.log_info(f'added consumer {name}')

    def get_message_type(self, name: str) -> Type[UniMessage]:
        if name in self._message_types:
            return self._message_types[name]

        self._message_types[name] = self.config.messages[name].type.import_class(UniMessage, self.echo, util=self._util)

        return self._message_types[name]

    def answer_to(self, worker_name: str, req_meta: UniMessageMeta, payload: Optional[Union[Dict[str, Any], UniMessageMeta, UniMessage]], *, unwrapped: bool) -> None:
        wd = self._config.workers[worker_name]
        if not wd.need_answer:
            if payload is not None:
                raise UniWorkFlowError(f'output message must be None because worker {wd.name} has no possibility to send output messages')
            return

        if payload is None:
            raise UniPayloadSerializationError('output message must be not empty')

        answ_meta: UniMessageMeta
        if isinstance(payload, UniMessageMeta):
            answ_meta = payload
        else:
            assert wd.answer_message is not None
            answ_message_type = self.get_message_type(wd.answer_message.name)
            payload_msg: UniMessage
            if isinstance(payload, answ_message_type):
                payload_msg = payload
            elif isinstance(payload, dict):
                try:
                    payload_msg = answ_message_type(**payload)  # type: ignore
                except Exception as e:  # noqa
                    raise UniPayloadSerializationError(str(e))
            else:
                raise UniPayloadSerializationError(f'output message has invalid type. {type(payload).__name__} was given')

            answ_meta = req_meta.create_child(payload_msg.dict(), unwrapped=unwrapped)

        b = self.get_broker(wd.broker.name)

        assert req_meta.answer_params is not None
        b.publish_answer(req_meta.answer_params, answ_meta)
        self.echo.log_info(f'worker {worker_name} answers to {req_meta.answer_params.topic}->{req_meta.answer_params.id} :: {answ_meta}')

    def send_to(
        self,
        worker_name: str,
        payload: Union[Dict[str, Any], UniMessage],
        *,
        parent_meta: Optional[UniMessageMeta] = None,
        answer_params: Optional[UniAnswerParams] = None,
        alone: bool = False,
    ) -> Optional[UniAnswerMessage[UniMessage]]:
        if worker_name not in self._worker_initialized_list:
            raise OverflowError(f'worker {worker_name} was not initialized')

        wd = self._config.workers[worker_name]

        message_type = self.get_message_type(wd.input_message.name)
        try:
            if isinstance(payload, message_type):
                payload_data = payload.dict()
            elif isinstance(payload, dict):
                payload_data = message_type(**payload).dict()  # type: ignore
            else:
                raise TypeError(f'data has invalid type.{type(payload).__name__} was given')
        except Exception as e:  # noqa
            raise UniPayloadSerializationError(str(e))

        br = self.get_broker(wd.broker.name)

        if parent_meta is not None:
            meta = parent_meta.create_child(payload_data, unwrapped=wd.input_unwrapped, answer_params=answer_params)
        else:
            meta = UniMessageMeta.create_new(payload_data, unwrapped=wd.input_unwrapped, answer_params=answer_params)

        if meta.need_answer and wd.need_answer:
            assert wd.answer_message is not None
            answ_meta = br.rpc_call(wd.topic, meta, alone=alone, max_delay_s=wd.answer_avg_delay_s * 3, unwrapped=wd.answer_unwrapped)
            if answ_meta is None:
                if alone:
                    return None
                raise OverflowError('system error. answer object must be specified')
            return UniAnswerMessage(answ_meta, self.get_message_type(wd.answer_message.name))

        meta_list = [meta]
        br.publish(wd.topic, meta_list, alone=alone)  # TODO: make it list by default
        self.echo.log_info(f"worker {wd.name} sent message to topic '{wd.topic}':: {meta_list}")
        return None

    def start_cron(self) -> None:
        cron_jobs = UniCronJob.mk_jobs_list(self.config.cron_tasks.values(), self)
        self.echo.log_debug(f'cron jobs defined: {", ".join(cj.task.name for cj in cron_jobs)}')

        prev_time = time()
        while True:
            now = time()
            if (now - prev_time) < 0.8:
                sleep(.1)  # delay for correct next iteration
                continue
            delay, jobs = UniCronJob.search_next_tasks(cron_jobs)
            if delay is None:
                self.echo.log_warning("no active cron tasks found")
                return
            self.echo.log_debug(f"sleep {delay} seconds before running the tasks: {[cj.task.name for cj in jobs]}")
            if delay > 0:
                sleep(delay)
            self.echo.log_info(f"run the tasks: {[cj.task.name for cj in jobs]}")
            prev_time = time()
            for cj in jobs:
                cj.send()

    def exit(self) -> None:
        for b in self._connected_brokers:
            b.close()
        self._connected_brokers = list()

    def start_consuming(self) -> None:
        brokers = set()
        for wn in self._consumers_list:
            wd = self._config.workers[wn]
            wc = self.get_worker_consumer(wn)

            br = self.get_broker(wd.broker.name)

            self.echo.log_info(f"worker {wn} start consuming")
            br.add_consumer(UniBrokerConsumer(
                topic=wd.topic,
                id=f'{wn}__{uuid4()}',
                group_id=wn,
                unwrapped=wd.input_unwrapped,
                message_handler=wc.process_message,
                prefetch_count=wd.prefetch_count,
            ))

            self.echo.log_info(f'consumer {wn} initialized')
            brokers.add(wd.broker.name)

        with soft_interruption(self._handle_interruption, self._handle_force_interruption, self._interruption_err):
            for bn in brokers:
                b = self.get_broker(bn)
                self._brokers_with_active_consumption.append(b)
                self.echo.log_info(f'broker {bn} consuming start')
                b.start_consuming()

    def _interruption_err(self, err: Exception) -> None:
        self.echo.log_error(str(err))
        raise err

    def _handle_force_interruption(self) -> None:
        self.echo.log_warning('force interruption detected')

    def _handle_interruption(self) -> None:
        self.echo.log_warning('interruption detected')
        for b in self._brokers_with_active_consumption:
            self.echo.log_debug(f'broker "{b.definition.name}" was notified about interruption')
            b.stop_consuming()
        self._brokers_with_active_consumption = list()
        self.echo.log_info('all brokers was notified about interruption')

    def get_compressor(self, name: str) -> Callable[[bytes], bytes]:
        if name in self._compression_modules:
            return self._compression_modules[name]
        if name in self._config.compression:
            c = self._config.compression[name]
            self._compression_modules[name] = c.encoder_type.import_function()
            return self._compression_modules[name]
        raise ValueError(f'compression of "{name}" is not supported')

    def get_decompressor(self, name: str) -> Callable[[bytes], bytes]:
        if name in self._decompression_modules:
            return self._decompression_modules[name]
        if name in self._config.compression:
            c = self._config.compression[name]
            self._decompression_modules[name] = c.decoder_type.import_function()
            return self._decompression_modules[name]
        raise ValueError(f'decompression of "{name}" is not supported')

    def decompress_message_body(self, compression: Optional[str], data: Union[str, bytes]) -> bytes:
        data_bytes: bytes
        if isinstance(data, str):
            data_bytes = bytes(data, encoding='utf-8')
        elif isinstance(data, bytes):
            data_bytes = data
        else:
            raise TypeError('invalid type')
        if compression is not None:
            decompressor = self.get_decompressor(compression)
            return decompressor(data_bytes)
        return data_bytes

    def compress_message_body(self, compression: Optional[str], data: Union[str, bytes]) -> bytes:
        data_bytes: bytes
        if isinstance(data, str):
            data_bytes = bytes(data, encoding='utf-8')
        elif isinstance(data, bytes):
            data_bytes = data
        else:
            raise TypeError('invalid type')
        if compression is not None:
            compressor = self.get_compressor(compression)
            return compressor(data_bytes)
        return data_bytes

    def parse_content_type(self, content_type: str, data: Union[bytes, str]) -> Dict[str, Any]:
        data_str: str
        if isinstance(data, str):
            data_str = data
        elif isinstance(data, bytes):
            data_str = data.decode('utf-8')
        else:
            raise TypeError('invalid type')

        parser = self.get_content_type_parser(content_type)
        return parser(data_str)

    def serialize_content_type(self, content_type: str, data: Dict[str, Any]) -> bytes:
        if not isinstance(data, dict):
            raise TypeError(f'invalid type of payload. must be dict, {type(data).__name__} was given')

        serializer = self.get_content_type_serializer(content_type)
        res = serializer(data)
        if isinstance(res, str):
            return res.encode('utf-8')
        return res

    def get_content_type_serializer(self, name: str) -> Callable[[Dict[str, Any]], Union[bytes, str]]:
        if name in self._content_type_serializers:
            return self._content_type_serializers[name]
        if name in self._config.codecs:
            c = self._config.codecs[name]
            self._content_type_serializers[name] = c.encoder_type.import_function()
            return self._content_type_serializers[name]
        raise ValueError(f'content_type "{name}" is not supported')

    def get_content_type_parser(self, name: str) -> Callable[[Union[bytes, str]], Dict[str, Any]]:
        if name in self._content_type_parsers:
            return self._content_type_parsers[name]
        if name in self._config.codecs:
            c = self._config.codecs[name]
            self._content_type_parsers[name] = c.decoder_type.import_function()
            return self._content_type_parsers[name]
        raise ValueError(f'content_type "{name}" is not supported')

    def add_worker_to_init_list(self, name: str, no_related: bool) -> None:
        if name not in self._config.workers:
            self.echo.exit_with_error(f'worker "{name}" is not found in config "{self.config.file}"')
        wd = self._config.workers[name]
        self._worker_init_list.add(name)
        for waiting in wd.waitings:
            if waiting.name not in self._waiting_initialized_list:
                self._waiting_init_list.add(waiting.name)
        self.add_broker_topic_to_init(wd.broker.name, wd.topic, False)
        self.add_broker_topic_to_init(wd.broker.name, wd.error_topic, False)
        self.add_broker_topic_to_init(wd.broker.name, wd.error_payload_topic, False)
        if wd.need_answer:
            self.add_broker_topic_to_init(wd.broker.name, wd.answer_topic, True)
        if not no_related:
            for wn in wd.output_workers:
                self._worker_init_list.add(wn)
                owd = self._config.workers[wn]
                self.add_broker_topic_to_init(owd.broker.name, owd.topic, False)

    def add_broker_topic_to_init(self, name: str, topic: str, is_answer: bool) -> None:
        if name in self._brokers_with_topics_initialized:
            if is_answer:
                if topic in self._brokers_with_topics_initialized[name].answer_topics:
                    return
            else:
                if topic in self._brokers_with_topics_initialized[name].topics:
                    return

        if name not in self._brokers_with_topics_to_init:
            self._brokers_with_topics_to_init[name] = UniBrokerInitRecipe(set(), set())

        if is_answer:
            self._brokers_with_topics_to_init[name].answer_topics.add(topic)
        else:
            self._brokers_with_topics_to_init[name].topics.add(topic)

    def initialize(self, create: bool = True) -> None:
        echo = self.echo.mk_child('initialize')
        for wn in self._worker_init_list:
            echo.log_info(f'worker "{wn}"', )
            self._worker_initialized_list.add(wn)
        self._worker_init_list = set()

        for waiting_name in self._waiting_init_list:
            self._config.waitings[waiting_name].wait(echo)
            echo.log_info(f'waiting "{waiting_name}"')
            self._waiting_initialized_list.add(waiting_name)
        self._waiting_init_list = set()

        if create:
            for bn, collection in self._brokers_with_topics_to_init.items():
                bd = self._config.brokers[bn]

                if bd.marked_as_external:
                    echo.log_debug(f'broker "{bn}" skipped because it external')
                    continue

                b = self.wait_for_broker_connection(bn)

                b.initialize(collection.topics, collection.answer_topics)
                echo.log_info(f'broker "{b.definition.name}" topics :: {collection.topics}')
                if len(collection.answer_topics) > 0:
                    echo.log_info(f'broker "{b.definition.name}" answer topics :: {collection.answer_topics}')

                if bn not in self._brokers_with_topics_initialized:
                    self._brokers_with_topics_initialized[bn] = UniBrokerInitRecipe(set(), set())
                for topic in collection.topics:
                    self._brokers_with_topics_initialized[bn].topics.add(topic)
                for topic in collection.answer_topics:
                    self._brokers_with_topics_initialized[bn].answer_topics.add(topic)
            self._brokers_with_topics_to_init = dict()

    def get_worker_consumer(self, worker: Union[Type['UniWorker[Any, Any]'], str], *, singleton: bool = True) -> UniWorkerConsumer[Any, Any]:
        wd = self._config.get_worker_definition(worker)
        if wd.marked_as_external:
            raise OverflowError(f'worker "{worker}" is external. you could not get it')
        if not singleton or wd.name not in self._worker_instance_indexes:
            assert wd.type is not None
            worker_type = wd.type.import_class(UniWorker, self.echo, util=self._util)
            self.echo.log_info(f'get_worker :: initialized worker "{wd.name}"')
            wc = UniWorkerConsumer(wd, self, worker_type)
        else:
            return self._worker_instance_indexes[wd.name]
        self._worker_instance_indexes[wd.name] = wc
        return wc

    @property
    def config(self) -> UniConfig:
        return self._config

    def wait_for_broker_connection(self, name: str) -> UniBroker[Any]:
        br = self.get_broker(name)
        for try_count in range(br.definition.retry_max_count):
            try:
                br.connect()
                self.echo.log_info(f'wait_for_broker_connection :: broker {br.definition.name} connected')
                self._connected_brokers.append(br)
                return br
            except ConnectionError as e:
                self.echo.log_info(f'wait_for_broker_connection :: broker {br.definition.name} retry to connect [{try_count}/{br.definition.retry_max_count}] : {e}')
                sleep(br.definition.retry_delay_s)
                continue
        raise ConnectionError(f'unavailable connection to {br.definition.name}')
