from uuid import uuid1

from confluent_kafka.cimpl import Consumer as _ConsumerImpl
from confluent_kafka.error import ConsumeError, KeyDeserializationError, ValueDeserializationError
from confluent_kafka.serialization import MessageField, SerializationContext, SerializationError

from ..schema_registry import ShoreDeserializer, SchemaRegistryClient


################################################################
# Deserializing Consumer
################################################################
class ShoreConsumer(_ConsumerImpl):
    def __init__(
        self,
        kafka_conf: dict,
        sr_conf: dict,
        group_id: str,
        client_id: str = None,
        auto_offset_reset: str = "smallest",
        parse_unknown_schema: bool = True,
        **extra_confs,
    ):
        """Shore Consumer

        (NOTE)
         No need predefined deserializer.

        :param kafka_conf: {"bootstrap.servers": <str>, "sasl.username": <str>, ...}
        :type kafka_conf: dict
        :param sr_conf: {"url": <str>, "basic.auth.user.info": <str>, ...}
        :type sr_conf: dict
        :param group_id: group id for consumer.
        :type group_id: str
        :param client_id: client id for app, defaults to None.
        :type client_id: str, optional
        :param auto_offset_reset: auto offset reset, defaults to "smallest"
        :type auto_offset_reset: str, optional
        """
        # set properties
        self.kafka_conf = kafka_conf
        self.sr_conf = sr_conf
        self.group_id = group_id
        self.client_id = client_id if client_id is not None else uuid1().hex[8:]
        self.auto_offset_reset = auto_offset_reset
        self.parse_unknown_schema = parse_unknown_schema
        self.extra_confs = extra_confs

        # for debug
        self._registry = SchemaRegistryClient(self.sr_conf)
        self._conf = {
            **self.kafka_conf,
            "group.id": self.group_id,
            "client.id": self.client_id,
            "auto.offset.reset": self.auto_offset_reset,
            **self.extra_confs,
        }

        # set deserializer
        self._key_deserializer = ShoreDeserializer(self._registry, parse_unknown_schema=self.parse_unknown_schema)
        self._value_deserializer = ShoreDeserializer(self._registry, parse_unknown_schema=self.parse_unknown_schema)

        super(ShoreConsumer, self).__init__(self._conf)

    def poll(self, timeout=-1):
        """[summary]

        :param timeout: defaults to -1
        :type timeout: int, optional
        :raises ConsumeError:
        :raises KeyDeserializationError:
        :raises ValueDeserializationError:
        :return:
        :rtype: [type]
        """
        # receive message
        msg = super(ShoreConsumer, self).poll(timeout)
        if msg is None:
            return None
        if msg.error() is not None:
            raise ConsumeError(msg.error(), kafka_message=msg)

        # deserialize key
        key = msg.key()
        if key is not None:
            try:
                key = self._key_deserializer(key)
            except Exception as se:
                raise KeyDeserializationError(exception=se, kafka_message=msg)
        msg.set_key(key)

        # deserializer value
        value = msg.value()
        if value is not None:
            try:
                value = self._value_deserializer(value)
            except Exception as se:
                raise ValueDeserializationError(exception=se, kafka_message=msg)
        msg.set_value(value)

        return msg

    def consume(self, num_messages=1, timeout=-1):
        """
        :py:func:`Consumer.consume` not implemented, use
        :py:func:`ShoreConsumer.poll` instead
        """
        raise NotImplementedError("We don't use it anymore!")
