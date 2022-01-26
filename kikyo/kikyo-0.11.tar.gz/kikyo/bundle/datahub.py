import datetime as dt
import io
import json
import pickle
from typing import Any

import pulsar
from fastavro import parse_schema, schemaless_writer, schemaless_reader

from kikyo import Kikyo
from kikyo.datahub import DataHub, Producer, Consumer, Message

record_schema = {
    'name': 'DataHubRecord',
    'namespace': 'kikyo.datahub',
    'type': 'record',
    'fields': [
        {'name': 'type', 'type': 'string'},
        {'name': 'data', 'type': 'bytes'}
    ]
}

parsed_record_schema = parse_schema(record_schema)


class PulsarBasedDataHub(DataHub):
    def __init__(self, client: Kikyo):
        settings = client.settings.deep('pulsar')
        if not settings:
            return

        self.tenant = settings.get('tenant', 'public')
        self.namespace = settings.get('namespace', 'default')
        self.pulsar = pulsar.Client(settings['service_url'])

        client.add_component('pulsar_datahub', self)

    def create_producer(self, topic: str) -> Producer:
        return PulsarBasedProducer(self, topic)

    def subscribe(
            self,
            topic: str,
            subscription_name: str = None,
            consumer_name: str = None,
            auto_ack: bool = True,
    ) -> Consumer:
        return PulsarBasedConsumer(
            self,
            topic,
            subscription_name=subscription_name,
            consumer_name=consumer_name,
            auto_ack=auto_ack,
        )

    def get_topic(self, name: str):
        return f'persistent://{self.tenant}/{self.namespace}/{name}'


class PulsarBasedProducer(Producer):
    def __init__(self, datahub: PulsarBasedDataHub, topic: str):
        super().__init__()
        self.producer = datahub.pulsar.create_producer(
            datahub.get_topic(topic),
            block_if_queue_full=True,
        )

    def send(
            self,
            record: Any,
            partition_key: str = None,
    ):
        data = MessageUtils.build(record)
        self.producer.send(
            data,
            partition_key=partition_key,
        )

    def close(self):
        self.producer.close()


class PulsarMessage(Message):
    def __init__(self, msg: pulsar.Message):
        self._msg = msg
        self._value = MessageUtils.extract_data(msg.data())
        self._publish_time = None

    @property
    def value(self) -> Any:
        return self._value

    @property
    def publish_time(self) -> dt.datetime:
        if self._publish_time is None:
            self._publish_time = dt.datetime.fromtimestamp(self._msg.publish_timestamp() / 1000)
        return self._publish_time


class PulsarBasedConsumer(Consumer):
    def __init__(
            self,
            datahub: PulsarBasedDataHub,
            topic: str,
            subscription_name: str = None,
            consumer_name: str = None,
            auto_ack: bool = True,
    ):
        super().__init__()
        self.consumer = datahub.pulsar.subscribe(
            datahub.get_topic(topic),
            consumer_type=pulsar.ConsumerType.KeyShared,
            subscription_name=subscription_name,
            consumer_name=consumer_name,
            initial_position=pulsar.InitialPosition.Earliest,
        )
        self._auto_ack = auto_ack

    def receive(self) -> Message:
        msg = self.consumer.receive()
        if self._auto_ack:
            self.consumer.acknowledge(msg)
        return PulsarMessage(msg)

    def close(self):
        self.consumer.close()

    def ack(self, msg: Message):
        assert isinstance(msg, PulsarMessage)
        self.consumer.acknowledge(msg._msg)


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, dt.datetime):
            return obj.isoformat()
        elif isinstance(obj, dt.date):
            return obj.isoformat()
        return super().default(obj)


class MessageUtils:
    ENCODING = 'utf-8'

    @classmethod
    def build(cls, data: Any) -> bytes:
        if isinstance(data, (dict, list)):
            dtype = 'json'
            data = json.dumps(
                data,
                ensure_ascii=False,
                cls=JSONEncoder,
            ).encode(encoding=cls.ENCODING)
        elif isinstance(data, bytes):
            dtype = 'bytes'
            data = data
        elif isinstance(data, str):
            dtype = 'str'
            data = data.encode(encoding=cls.ENCODING)
        else:
            dtype = 'object'
            data = pickle.dumps(data)

        d = {
            'type': dtype,
            'data': data,
        }
        wio = io.BytesIO()
        schemaless_writer(wio, parsed_record_schema, d)
        return wio.getvalue()

    @classmethod
    def extract_data(cls, content: bytes) -> Any:
        message = schemaless_reader(io.BytesIO(content), parsed_record_schema)
        if message['type'] == 'json':
            return json.loads(message['data'].decode(encoding=cls.ENCODING))
        if message['type'] == 'bytes':
            return message['data']
        if message['type'] == 'str':
            return message['data'].decode(encoding=cls.ENCODING)
        if message['type'] == 'object':
            return pickle.loads(message['data'])
