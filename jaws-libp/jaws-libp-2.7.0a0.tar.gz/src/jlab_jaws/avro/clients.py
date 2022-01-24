"""
    Clients for interacting with JAWS entities.
"""
import logging
import os
import signal
import time
from typing import Dict, Any

from confluent_kafka import Message, SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from tabulate import tabulate

from jlab_jaws.avro.entities import UnionEncoding
from jlab_jaws.avro.serde import LocationSerde, OverrideKeySerde, OverrideSerde, EffectiveRegistrationSerde, \
    StringSerde, Serde, EffectiveAlarmSerde, EffectiveActivationSerde, ClassSerde, ActivationSerde, InstanceSerde
from jlab_jaws.eventsource.listener import EventSourceListener
from jlab_jaws.eventsource.cached_table import CachedTable

logger = logging.getLogger(__name__)


def set_log_level_from_env():
    level = os.environ.get('LOGLEVEL', 'WARNING').upper()
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(threadName)-16s %(name)s %(message)s',
        level=level,
        datefmt='%Y-%m-%d %H:%M:%S')


def get_registry_client():
    sr_conf = {'url': os.environ.get('SCHEMA_REGISTRY', 'http://localhost:8081')}
    return SchemaRegistryClient(sr_conf)


class MonitorListener(EventSourceListener):

    def on_highwater_timeout(self) -> None:
        pass

    def on_batch(self, msgs: Dict[Any, Message]) -> None:
        for msg in msgs.values():
            print("{}={}".format(msg.key(), msg.value()))

    def on_highwater(self) -> None:
        pass


class JAWSConsumer(CachedTable):

    def __init__(self, topic, client_name, key_serde, value_serde):
        self._topic = topic
        self._client_name = client_name
        self._key_serde = key_serde
        self._value_serde = value_serde

        set_log_level_from_env()

        signal.signal(signal.SIGINT, self.__signal_handler)

        ts = time.time()

        bootstrap_servers = os.environ.get('BOOTSTRAP_SERVERS', 'localhost:9092')
        config = {'topic': topic,
                  'bootstrap.servers': bootstrap_servers,
                  'key.deserializer': key_serde.deserializer(),
                  'value.deserializer': value_serde.deserializer(),
                  'group.id': client_name + str(ts)}

        super().__init__(config)

    def print_records_continuous(self):
        self.add_listener(MonitorListener())
        self.start()

    def print_table(self, head=None, msg_to_list=lambda msg: list(), nometa=False, filter_if=lambda key, value: True):
        if head is None:
            head = []
        records = self.get_records()

        table = []

        if not nometa:
            head = ["Timestamp", "User", "Host", "Produced By"] + head

        for record in records.values():
            row = self.__get_row(record, msg_to_list, filter_if, nometa)
            if row is not None:
                table.append(row)

        # Truncate long cells
        table = [[(c if len(str(c)) < 30 else str(c)[:27] + "...") for c in row] for row in table]

        print(tabulate(table, head))

    def export_records(self, filter_if=lambda key, value: True):
        records = self.get_records()

        sortedtuples = sorted(records.items())

        for item in sortedtuples:
            key = item[1].key()
            value = item[1].value()

            if filter_if(key, value):
                key_json = self._key_serde.to_json(key)
                value_json = self._value_serde.to_json(value)

                print(key_json + '=' + value_json)

    def get_records(self) -> Dict[Any, Message]:
        self.start()
        records = self.await_get(5)
        self.stop()
        return records

    def consume(self, monitor=False, nometa=False, export=False, head=None,
                msg_to_list=lambda msg: list(), filter_if=lambda key, value: True):
        if monitor:
            self.print_records_continuous()
        elif export:
            self.export_records(filter_if)
        else:
            self.print_table(head, msg_to_list, nometa, filter_if)

    def __get_row(self, msg: Message, msg_to_list, filter_if, nometa: bool):
        timestamp = msg.timestamp()
        headers = msg.headers()

        row = msg_to_list(msg)

        if filter_if(msg.key(), msg.value()):
            if not nometa:
                row_header = self.__get_row_header(headers, timestamp)
                row = row_header + row
        else:
            row = None

        return row

    @staticmethod
    def __get_row_header(headers, timestamp):
        ts = time.ctime(timestamp[1] / 1000)

        user = ''
        producer = ''
        host = ''

        if headers is not None:
            lookup = dict(headers)
            bytez = lookup.get('user', b'')
            user = bytez.decode()
            bytez = lookup.get('producer', b'')
            producer = bytez.decode()
            bytez = lookup.get('host', b'')
            host = bytez.decode()

        return [ts, user, host, producer]

    def __signal_handler(self, sig, frame):
        print('Stopping from Ctrl+C!')
        self.stop()


class JAWSProducer:
    """
        This class produces messages with the JAWS expected header.

        Sensible defaults are used to determine BOOTSTRAP_SERVERS (look in env)
        and to handle errors (log them).

        This producer also knows how to import records from a file using the JAWS expected file format.
    """

    def __init__(self, topic: str, client_name: str, key_serde: Serde, value_serde: Serde):
        set_log_level_from_env()

        self._topic = topic
        self._client_name = client_name

        key_serializer = key_serde.serializer()
        value_serializer = value_serde.serializer()

        bootstrap_servers = os.environ.get('BOOTSTRAP_SERVERS', 'localhost:9092')
        producer_conf = {'bootstrap.servers': bootstrap_servers,
                         'key.serializer': key_serializer,
                         'value.serializer': value_serializer}

        self._producer = SerializingProducer(producer_conf)
        self._headers = self.__get_headers()

    def send(self, key, value):
        logger.debug("{}={}".format(key, value))
        self._producer.produce(topic=self._topic, headers=self._headers, key=key, value=value,
                               on_delivery=self.__on_delivery)
        self._producer.flush()

    def import_records(self, file, line_to_kv):
        logger.debug("Loading file", file)
        handle = open(file, 'r')
        lines = handle.readlines()

        for line in lines:
            key, value = line_to_kv(line)

            logger.debug("{}={}".format(key, value))
            self._producer.produce(topic=self._topic, headers=self._headers, key=key, value=value,
                                   on_delivery=self.__on_delivery)

        self._producer.flush()

    def __get_headers(self):
        return [('user', os.getlogin()),
                ('producer', self._client_name),
                ('host', os.uname().nodename)]

    @staticmethod
    def __on_delivery(err, msg):
        if err is not None:
            logger.error('Failed: {}'.format(err))
        else:
            logger.debug('Delivered')


class ActivationConsumer(JAWSConsumer):
    def __init__(self, client_name: str):
        schema_registry_client = get_registry_client()
        key_serde = StringSerde()
        value_serde = ActivationSerde(schema_registry_client)

        super().__init__('alarm-activations', client_name, key_serde, value_serde)


class CategoryConsumer(JAWSConsumer):
    def __init__(self, client_name: str):
        key_serde = StringSerde()
        value_serde = StringSerde()

        super().__init__('alarm-categories', client_name, key_serde, value_serde)


class ClassConsumer(JAWSConsumer):
    def __init__(self, client_name: str):
        schema_registry_client = get_registry_client()
        key_serde = StringSerde()
        value_serde = ClassSerde(schema_registry_client)

        super().__init__('alarm-classes', client_name, key_serde, value_serde)


class EffectiveActivationConsumer(JAWSConsumer):
    def __init__(self, client_name: str):
        schema_registry_client = get_registry_client()
        key_serde = StringSerde()
        value_serde = EffectiveActivationSerde(schema_registry_client)

        super().__init__('effective-activations', client_name, key_serde, value_serde)


class EffectiveAlarmConsumer(JAWSConsumer):
    def __init__(self, client_name: str):
        schema_registry_client = get_registry_client()
        key_serde = StringSerde()
        value_serde = EffectiveAlarmSerde(schema_registry_client)

        super().__init__('effective-alarms', client_name, key_serde, value_serde)


class EffectiveRegistrationConsumer(JAWSConsumer):
    def __init__(self, client_name: str):
        schema_registry_client = get_registry_client()
        key_serde = StringSerde()
        value_serde = EffectiveRegistrationSerde(schema_registry_client)

        super().__init__('effective-registrations', client_name, key_serde, value_serde)


class InstanceConsumer(JAWSConsumer):
    def __init__(self, client_name: str):
        schema_registry_client = get_registry_client()
        key_serde = StringSerde()
        value_serde = InstanceSerde(schema_registry_client, UnionEncoding.DICT_WITH_TYPE)

        super().__init__('alarm-instances', client_name, key_serde, value_serde)


class LocationConsumer(JAWSConsumer):
    def __init__(self, client_name: str):
        schema_registry_client = get_registry_client()
        key_serde = StringSerde()
        value_serde = LocationSerde(schema_registry_client)

        super().__init__('alarm-locations', client_name, key_serde, value_serde)


class OverrideConsumer(JAWSConsumer):
    def __init__(self, client_name: str):
        schema_registry_client = get_registry_client()
        key_serde = StringSerde()
        value_serde = OverrideSerde(schema_registry_client)

        super().__init__('alarm-overrides', client_name, key_serde, value_serde)


class ActivationProducer(JAWSProducer):
    def __init__(self, client_name: str):
        schema_registry_client = get_registry_client()
        key_serde = StringSerde()
        value_serde = ActivationSerde(schema_registry_client)

        super().__init__('alarm-activations', client_name, key_serde, value_serde)


class CategoryProducer(JAWSProducer):
    def __init__(self, client_name: str):
        key_serde = StringSerde()
        value_serde = StringSerde()

        super().__init__('alarm-categories', client_name, key_serde, value_serde)


class ClassProducer(JAWSProducer):
    def __init__(self, client_name: str):
        schema_registry_client = get_registry_client()
        key_serde = StringSerde()
        value_serde = ClassSerde(schema_registry_client)

        super().__init__('alarm-classes', client_name, key_serde, value_serde)


class EffectiveActivationProducer(JAWSProducer):
    def __init__(self, client_name: str):
        schema_registry_client = get_registry_client()
        key_serde = StringSerde()
        value_serde = EffectiveActivationSerde(schema_registry_client)

        super().__init__('effective-activations', client_name, key_serde, value_serde)


class EffectiveAlarmProducer(JAWSProducer):
    def __init__(self, client_name: str):
        schema_registry_client = get_registry_client()
        key_serde = StringSerde()
        value_serde = EffectiveAlarmSerde(schema_registry_client)

        super().__init__('effective-alarms', client_name, key_serde, value_serde)


class EffectiveRegistrationProducer(JAWSProducer):
    def __init__(self, client_name: str):
        schema_registry_client = get_registry_client()
        key_serde = StringSerde()
        value_serde = EffectiveRegistrationSerde(schema_registry_client)

        super().__init__('effective-registrations', client_name, key_serde, value_serde)


class InstanceProducer(JAWSProducer):
    def __init__(self, client_name: str):
        schema_registry_client = get_registry_client()
        key_serde = StringSerde()
        value_serde = InstanceSerde(schema_registry_client)

        super().__init__('alarm-instances', client_name, key_serde, value_serde)


class LocationProducer(JAWSProducer):
    def __init__(self, client_name: str):
        schema_registry_client = get_registry_client()
        key_serde = StringSerde()
        value_serde = LocationSerde(schema_registry_client)

        super().__init__('alarm-locations', client_name, key_serde, value_serde)


class OverrideProducer(JAWSProducer):
    def __init__(self, client_name: str):
        schema_registry_client = get_registry_client()
        key_serde = OverrideKeySerde(schema_registry_client)
        value_serde = OverrideSerde(schema_registry_client)

        super().__init__('alarm-overrides', client_name, key_serde, value_serde)
