# -*- coding: UTF-8 -*-
# @Time : 2021/12/1 下午4:04 
# @Author : 刘洪波
import pulsar
import json
import time
from pulsar_mq.Producers import Producer
from pulsar_mq.Consumers import Consumer

"""
pulsar服务
一、 ConsumeProduce
1. 订阅pulsar
2. 处理消费的数据
3. 发送业务数据
4. 发送的 队列 可以是 随机的

二、 ProduceConsume

1. 发送数据至pulsar
2. 订阅pulsar得到业务数据
3. 消费的 队列 可以是 随机的
"""


class ConsumeProduce(object):
    """订阅得到业务数据，经处理过后发送"""

    def __init__(self, client, consumer_topic, consumer_name: str, producer_topic=None,
                 schema=pulsar.schema.StringSchema()):
        """
        创建 生产者 和 消费者
        :param client:
        :param consumer_topic:
        :param consumer_name:
        :param producer_topic:
        :param schema:
        """
        self.client = client
        self.sch = schema
        self.consumer = Consumer(client, consumer_topic, consumer_name, schema=schema)
        if producer_topic:
            self.producer = Producer(client, producer_topic, schema=schema)
        else:
            self.producer = None

    def run(self, task, thread_count=None, _async=True, callback=None, logger=None):
        """
        :param task: 任务程序
        :param thread_count: 指定最大线程数
        :param _async: 是否异步发送消息， True异步发送， Flase 同步发送
        :param callback: 异步发送的回调函数
        :param logger: 日志收集器
        :return:
        """

        def send_task(msg):
            result = task(msg)
            data = json.loads(msg.data())
            random_topic = data.get('random_topic')
            if random_topic:
                producer = Producer(self.client, random_topic, schema=self.sch)
                producer.send(result, _async=_async, callback=callback)
                producer.close()
            elif self.producer:
                self.producer.send(result, _async=_async, callback=callback)
            else:
                raise ValueError('producer_topic and random_topic is None, need producer topic')

        self.consumer.receive(send_task, thread_count, logger)


class ProduceConsume(object):
    """发送数据至pulsar，订阅pulsar得到业务数据"""

    def __init__(self, client, producer_topic, consumer_topic=None, consumer_name=None,
                 schema=pulsar.schema.StringSchema()):
        self.client = client
        self.sch = schema
        self.consumer_topic = consumer_topic
        self.consumer_name = consumer_name
        self.producer = Producer(client, producer_topic, schema=schema)

    def run(self, data, random_topic=True, timeout_millis=300000, _async=True, callback=None):
        """
        :param data: 输入格式为json
        :param random_topic: 是否随机队列
        :param timeout_millis: 订阅超时
        :param _async: 是否异步发送消息， True异步发送， Flase 同步发送
        :param callback: 异步发送的回调函数
        :return:
        """
        if random_topic:
            random_topic = 'cdss_random_topic_' + str(int(round(time.time() * 1000000)))
            self.consumer_topic = random_topic
            self.consumer_name = random_topic
        if self.consumer_topic and self.consumer_name:
            consumer = self.client.subscribe(self.consumer_topic, self.consumer_name, schema=self.sch)
            self.producer.send(data, _async=_async, callback=callback, random_topic=random_topic)
            msgs = []
            if isinstance(data, list):
                for i in range(len(data)):
                    msg = consumer.receive(timeout_millis)
                    consumer.acknowledge(msg)
                    msgs.append(msg)
                consumer.close()
                return msgs
            elif isinstance(data, str):
                msg = consumer.receive(timeout_millis)
                consumer.acknowledge(msg)
                consumer.close()
                return msg
            else:
                raise ValueError('the data type sent is wrong, the required type is list or str')
        else:
            raise ValueError('consumer_topic and random_topic is None, need consumer topic')
