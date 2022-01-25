# #!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022/1/24 16:38
# @Author : BruceLong
# @FileName: x_kafka.py
# @Email   : 18656170559@163.com
# @Software: PyCharm
# @Blog ：http://www.cnblogs.com/yunlongaimeng/
import json

from kafka import KafkaProducer
from kafka.errors import KafkaError
from .config import KAFKA_HOST, KAFKA_PORT, KAFKA_TOPIC
from .x_single import SingletonType


class XKafka(metaclass=SingletonType):

    def __init__(self, host: str = KAFKA_HOST, port: str = KAFKA_PORT, kafka_topic=KAFKA_TOPIC):
        self.host = host
        self.port = port
        self.kafka_topic = kafka_topic
        self.connect_sign = 0

    def _connect(self):
        self.__producer = KafkaProducer(bootstrap_servers='{kafka_host}:{kafka_port}'.format(
            kafka_host=self.host,
            kafka_port=self.port,
        ))
        return self.__producer

    def insert(self, item, **kwargs):
        '''
        topic, value=None, key=None, partition=None, timestamp_ms=None
        :param item:
        :param kwargs:
        :return:
        '''
        if not self.connect_sign:
            self._connect()
        parmas_message = json.dumps(dict(item))
        try:
            self.__producer.send(topic=self.kafka_topic, value=parmas_message.encode('utf-8'), **kwargs)
            self.__producer.flush()
            return item
        except KafkaError as e:
            raise e


x_kafka = XKafka()
