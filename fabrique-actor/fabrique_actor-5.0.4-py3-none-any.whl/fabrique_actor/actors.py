import confluent_kafka
from .env2configs import AdminConf, ProdConf, ConsConf
import os
from .kafka_admin import Admin
import signal
from .message import StandaloneActorMetricsMessage as MetricsMessage
import sys
from typing import Optional, Tuple, Union
from time import time, sleep

from .logger import Logger

from collections import namedtuple

RawMes = namedtuple('RawMes', ['value', 'key'])
RawMesWDest = namedtuple('RawMesWDest', ['value', 'key', 'topic_out'])


def _get_messages2process(msgs):
    msgs2process = []
    for msg in msgs:
        if msg.error():
            # noinspection PyProtectedMember
            if msg.error().code() == confluent_kafka.KafkaError._PARTITION_EOF:
                pass
            if msg.error().code() == confluent_kafka.KafkaError.UNKNOWN_TOPIC_OR_PART:
                print(f"! Sort of wtf error {msg.error()}")
            else:
                raise Exception(msg.error())
        else:
            # Proper message
            msgs2process.append(msg)

    return msgs2process


class _StandaloneActor:
    def __init__(self, has_consumer_loop=True, has_output_stream=True, is_dispatcher=False):
        """
        """

        admin_conf = AdminConf()
        self.admin = None

        self.client_id = os.environ.get('HOSTNAME')
        self.logger = Logger.make_logger(self.client_id)

        prod_conf = ProdConf(sends_to_topic_out=has_output_stream, is_dispatcher=is_dispatcher)

        self.consumer = None  # emitter works w/o consumer for example
        self.producer = confluent_kafka.Producer(prod_conf.configs)

        self.topic_out = prod_conf.topic_out if has_output_stream else None
        self.topic_out_dict = prod_conf.topic_out_dict if has_output_stream else None

        self.running = True

        if has_consumer_loop:
            cons_conf = ConsConf()
            self.consumer = confluent_kafka.Consumer(cons_conf.configs)
            self.topic_in = cons_conf.topic_in

            self.consumer.subscribe([topic.strip() for topic in self.topic_in.split(',')])

            signal.signal(signal.SIGTERM, self.close)
            signal.signal(signal.SIGINT, self.close)

            self.consumer_num_messages = cons_conf.consumer_num_messages
            self.consumer_timeout_s = cons_conf.consumer_timeout_s

        self.metrics_topic = admin_conf.metrics_topic

        self.post_init(admin_conf, has_output_stream)

    def post_init(self, admin_conf, has_output_stream):
        if not admin_conf.kafka_def_auto_topics:
            self.admin = Admin(admin_conf.configs)

            if has_output_stream:
                self._create_out_topic(admin_conf)

            if self.metrics_topic:
                self._create_metrics_topic(admin_conf)

    def close(self, _arg1, _arg2):
        self.running = False

    def _create_metrics_topic(self, admin_conf):
        self.admin.create_or_update_topic(self.metrics_topic,
                                          10,
                                          admin_conf.replication,
                                          {'retention.ms': str(admin_conf.metrics_retention_ms),
                                           'retention.bytes': str(admin_conf.metrics_retention_bytes)
                                           })

    def _create_out_topic(self, admin_conf):
        num_partitions = admin_conf.partitions
        replication = admin_conf.replication
        retention_ms = admin_conf.retention_ms
        retention_bytes = admin_conf.retention_bytes

        if not num_partitions:
            topic_in_cfg = self.admin.get_topics_configs([self.topic_in, ])[self.topic_in]
            if not topic_in_cfg:
                raise Exception(f'Input topic {self.topic_in} not found')

            num_partitions = topic_in_cfg['num_partitions']

        self.admin.create_topic_with_params(self.topic_out,
                                            num_partitions,
                                            replication,
                                            {'retention.ms': str(retention_ms),
                                             'retention.bytes': str(retention_bytes)
                                             })

    def send_metrics(self, metrics=None, alerts=None, error=None, session_id=None):
        """
        sends fabrique metric message to FABRIQUE_METRIC_COLLECTOR_TOPIC

        :param metrics:
        :param alerts:
        :param error:
        :param session_id:
        """
        mes = MetricsMessage(self.client_id, metrics=metrics, alerts=alerts, error=error, session_id=session_id)
        self.send(self.metrics_topic, value=mes.serialize())

    def send(self, topic_out, value, key=None):
        while True:
            try:
                self.producer.produce(topic_out, value=value, key=key)
                break
            except BufferError:
                print('waiting for send buffer cleaning')
                self.producer.flush()

    def process_raw_messages_list(self, msgs2process: list) -> None:
        raise Exception("This method needs to be defined in a subclass with consumer loop")

    def start(self):
        """
        Starts consumer loop
        """
        print("start")

        try:
            while self.running:
                msgs = self.consumer.consume(num_messages=self.consumer_num_messages,
                                             timeout=self.consumer_timeout_s)
                if not msgs:
                    continue

                # print(msgs)
                msgs2process = _get_messages2process(msgs)

                if not msgs2process:
                    continue

                self.process_raw_messages_list(msgs2process)

        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')

        finally:
            # Close down consumer to commit final offsets.
            self.consumer.close()
            print('consumer closed')


class Processor(_StandaloneActor):
    def __init__(self):
        """
            Processor gets messages from TOPIC_IN kafka topic, makes custom manipulations by
            custom process_message (process_raw_message or process_raw_messages_list) method
            and sends result to TOPIC_OUT kafka topic
        """
        super().__init__()

    def process_raw_message(self, msg) -> RawMes:
        """
        by default uses process_message(msg.value()) to process binary message body
        then creates RawMes (.value with message body, and .key with kafka key)

        You can redefine this method for complex logic on msg.topic(), msg.key(), ...

        :param msg: confluent_kafka.Message objects from consumer
        :return: RawMes
        """
        value = self.process_message(msg.value())
        raw_mes = RawMes(key=msg.key(), value=value)
        return raw_mes

    def process_raw_messages_list(self, msgs2process: list) -> None:
        """
        by default uses process_raw_message(msg) to process msgs2process element (confluent_kafka.Message type)
        then sends result to TOPIC_OUT

        You can redefine this method for custom batch processing, and/or complex logic on msg.topic(), msg.key(), ...

        :param msgs2process: list of confluent_kafka.Message objects from consumer
        """

        results = [self.process_raw_message(msg) for msg in msgs2process]
        for res in results:
            if res.value is None:
                continue
            self.send(self.topic_out, res.value, res.key)

    def process_message(self, mes_body: bytes) -> Optional[bytes]:
        """
        Your method of:
        1. Deserialization (for example json.loads())
        2. Processing
        3. Serialization (for example json.dumps())
        if returns None, nothing will be sent to TOPIC_OUT

        :param mes_body: serialized message body in bytes
        :return: serialized message body in bytes
        """
        raise Exception("This method needs to be defined in a subclass")


class Collector(_StandaloneActor):
    def __init__(self):
        """
            Collector gets messages from TOPIC_IN kafka topic and makes custom manipulations by
            custom process_message (process_raw_message or process_raw_messages_list) method
        """
        super().__init__(has_output_stream=False)

    def process_raw_messages_list(self, msgs2process: list) -> None:
        """
        by default uses process_raw_message(msg) to process msgs2process element (confluent_kafka.Message type)

        You can redefine this method for custom batch processing, and/or complex logic on msg.topic(), msg.key(), ...

        :param msgs2process: list of confluent_kafka.Message objects from consumer
        """

        for msg in msgs2process:
            self.process_raw_message(msg)

    def process_raw_message(self, msg) -> None:
        """
        by default uses process_message(msg.value()) to process binary message body

        You can redefine this method for complex logic on msg.topic(), msg.key(), ...

        :param msg: confluent_kafka.Message objects from consumer
        """
        self.process_message(msg.value())

    def process_message(self, mes_body: bytes):
        """
        Your method of:
        1. Deserialization (for example json.loads())
        2. Processing

        :param mes_body: serialized message body in bytes
        """
        raise Exception("This method needs to be defined in a subclass")


class Emitter(_StandaloneActor):
    def __init__(self):
        """
            Emitter sends messages to TOPIC_OUT and metrics to FABRIQUE_METRIC_COLLECTOR_TOPIC,
            and hasn't consumer loop
        """
        super().__init__(has_consumer_loop=False)

    def send_mes(self, value, key=None):
        """
        sends messages to TOPIC_OUT

        :param value: serialized message body in bytes
        :param key: message key in bytes
        """
        self.send(self.topic_out, value, key)

    def create_message(self):
        """returns value, key in bytes"""
        raise Exception("This method needs to be defined in a subclass")

    def start(self):
        """
        if EMITTER_TPS envvar is set it will sleep some amount of time to provide selected transactions per second
        (messages per second)
        """
        EMITTER_TPS = int(os.getenv("EMITTER_TPS", '0'))

        print(f'EMITTER_TPS = {EMITTER_TPS}')
        if not EMITTER_TPS:
            # if EMITTER_TPS is not set
            while self.running:
                value, key = self.create_message()
                self.send_mes(value, key)
            return

        while self.running:
            t = time()
            for _ in range(EMITTER_TPS):
                value, key = self.create_message()
                self.send_mes(value, key)
            sending_time = time()-t
            sleep_time = 1.0 - sending_time
            if sleep_time < 0:
                self.logger.error(f"Can't provide desired TPS, {EMITTER_TPS} > {EMITTER_TPS/sending_time} ")
                continue
            sleep(sleep_time)



class Dispatcher(_StandaloneActor):
    def __init__(self):
        """
            Dispatcher gets messages from TOPIC_IN kafka topic, makes custom manipulations by
            custom process_message (process_raw_message or process_raw_messages_list) method
            and sends result to one of destinations in TOPIC_OUT_DICT ({destination_id0: topic0, ...})
        """
        super().__init__(has_output_stream=True, is_dispatcher=True)

        keys, topics = zip(*self.topic_out_dict.items())
        self.destinations = namedtuple('destinations', keys)(*topics)


    def process_raw_message(self, msg) -> RawMesWDest:
        """
        by default uses process_message(msg.value()) to process binary message body
        then creates RawMes (.value with message body, and .key with kafka key)

        You can redefine this method for complex logic on msg.topic(), msg.key(), ...

        :param msg: confluent_kafka.Message objects from consumer
        :return: 'RawMesWDest'
        """
        value, topic_out = self.process_message(msg.value())
        raw_mes_w_dest = RawMesWDest(key=msg.key(), value=value, topic_out=topic_out)
        return raw_mes_w_dest

    def process_raw_messages_list(self, msgs2process: list) -> None:
        """
        by default uses process_raw_message(msg) to process msgs2process element (confluent_kafka.Message type)
        then sends result to TOPIC_OUT

        You can redefine this method for custom batch processing, and/or complex logic on msg.topic(), msg.key(), ...

        :param msgs2process: list of confluent_kafka.Message objects from consumer
        """

        results = [self.process_raw_message(msg) for msg in msgs2process]
        for res in results:
            if res.value is None:
                continue
            if res.topic_out is None:
                continue
            self.send(res.topic_out, res.value, res.key)

    def process_message(self, mes_body: bytes) -> Tuple[Union[bytes, None], Union[str, None]]:
        """
        Your method of:
        1. Deserialization (for example json.loads())
        2. Processing
        3. Serialization (for example json.dumps())
        4. Pick destination
        if returns (None, None), (None, str), (bytes, None) nothing will be sent to output topics
        your TOPIC_OUT_DICT env looks like json string {"destination_id1": "dest_topic1",
        "destination_id2": "dest_topic2", ...}

        :param mes_body: serialized message body in bytes
        :return: (serialized message body in bytes, destination_id str)
        """
        raise Exception("This method needs to be defined in a subclass")
