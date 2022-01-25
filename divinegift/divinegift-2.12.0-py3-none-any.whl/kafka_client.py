from typing import Optional

from divinegift import main
from divinegift import logger
from divinegift.errors import ProducerNotSetError, ConsumerNotSetError

try:
    from confluent_kafka import Producer, Consumer, KafkaError, TopicPartition
    from confluent_kafka import OFFSET_STORED, OFFSET_BEGINNING, OFFSET_END
except ImportError:
    raise ImportError("confluent_kafka isn't installed. Run: pip install -U confluent_kafka")
try:
    from confluent_kafka import avro
    from confluent_kafka.avro import AvroProducer, AvroConsumer
    from confluent_kafka.avro.serializer import SerializerError
    from confluent_kafka.avro.error import ClientError
except ImportError:
    pass
try:
    from divinegift.string_avro import StringAvroConsumer
except NameError:
    pass


class KafkaClient:
    def __init__(self, logger_: Optional[logger.Logger] = None):
        self.producer = None
        self.avro_producer = False
        self.consumer = None
        self.avro_consumer = False
        self.logger = logger_ if logger_ else logger.Logger()

    def set_producer(self, **configs):
        self.producer = Producer(**configs)

    def set_producer_avro(self, value_schema: str, **configs):
        try:
            self.producer = AvroProducer({**configs}, default_value_schema=avro.loads(value_schema))
            self.avro_producer = True
        except NameError:
            raise Exception("confluent_kafka isn't installed. Run: pip install -U confluent_kafka[avro]")
        except ClientError as ex:
            raise ClientError(str(ex))

    def close_producer(self):
        if self.producer:
            self.producer.close()
            self.producer = None
            self.avro_producer = False
        else:
            raise ProducerNotSetError('Set consumer before!')

    def set_consumer(self, **configs):
        self.consumer = Consumer(**configs)

    def set_consumer_avro(self, key_string=False, **configs):
        try:
            if key_string:
                self.consumer = StringAvroConsumer({**configs})
            else:
                self.consumer = AvroConsumer({**configs})
            self.avro_consumer = True
        except NameError:
            raise Exception("confluent_kafka isn't installed. Run: pip install -U confluent_kafka[avro]")
        except ClientError as ex:
            raise ClientError(str(ex))

    def close_consumer(self):
        if self.consumer:
            self.consumer.close()
            self.consumer = None
            self.avro_consumer = False
        else:
            raise ConsumerNotSetError('Set consumer before!')

    def delivery_report(self, err, msg):
        """ Called once for each message produced to indicate delivery result.
            Triggered by poll() or flush(). """
        if err is not None:
            self.logger.log_info(f'Message delivery to {msg.topic()} failed: {err}')
            self.logger.log_debug(dir(msg))
            self.logger.log_debug(msg)
        else:
            self.logger.log_info(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    def send_message(self, topic, messages):
        def produce(topic, message):
            self.producer.poll(0)
            if isinstance(message, str):
                self.producer.produce(topic=topic, value=message.encode('utf-8'), callback=self.delivery_report)
            elif not self.avro_producer:
                if isinstance(message, dict):
                    json_obj = main.Json()
                    json_obj.set_data(message)
                    self.producer.produce(topic=topic, value=json_obj.dumps().encode('utf-8'),
                                          callback=self.delivery_report)
            else:
                self.producer.produce(topic=topic, value=message, callback=self.delivery_report)

        if self.producer is not None:
            if isinstance(messages, list):
                for message in messages:
                    produce(topic, message)
            else:
                produce(topic, messages)
            self.producer.flush()
        else:
            raise ProducerNotSetError('Set producer before!')

    def set_offset(self, topic: str, partition: int, offset: int):
        if self.consumer:
            topic_p = TopicPartition(topic, partition, offset)

            self.consumer.assign([topic_p])
            self.consumer.seek(topic_p)
            # self.consumer.commit(offsets=[topic_p])
        else:
            raise ConsumerNotSetError('Set consumer before!')

    def read_messages(self, topic, partition=None, offset=OFFSET_STORED):
        if self.consumer:
            if partition is not None and offset != OFFSET_STORED :
                self.set_offset(topic, partition, offset)
            else:
                self.consumer.subscribe([topic])

            while True:
                try:
                    msg = self.consumer.poll(10)
                except SerializerError as e:
                    self.logger.log_err(f"Message deserialization failed: {e}")
                    continue
                if msg is None:
                    continue
                if msg.error():
                    self.logger.log_err(f"{'Avro' if self.avro_consumer else ''}Consumer error: {msg.error()}")
                    continue
                self.logger.log_info(f'Message recieved from {msg.topic()} [{msg.partition()}]')
                self.logger.log_debug(f'Received message: {msg.value()}')
                if self.avro_consumer:
                    yield msg.value()
                else:
                    yield msg.value().decode('utf-8')
        else:
            raise ConsumerNotSetError('Set consumer before!')


if __name__ == '__main__':
    pass
