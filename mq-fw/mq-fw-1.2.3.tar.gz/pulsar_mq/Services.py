# -*- coding: UTF-8 -*-
# @Time : 2021/12/1 下午4:04 
# @Author : 刘洪波
import pulsar
from pulsar_mq.Producers import Producer
from pulsar_mq.Consumers import Consumer

"""
pulsar服务
一、 ConsumeProduce
1. 订阅pulsar
2. 处理消费的数据
3. 发送业务数据

二、 ProduceConsume

1. 发送数据至pulsar
2. 订阅pulsar得到业务数据
"""


class ConsumeProduce(object):
    """订阅得到业务数据，经处理过后发送"""
    def __init__(self, client, producer_topic: str, consumer_topic, consumer_name: str, schema):
        """
        创建 生产者 和 消费者
        :param client:
        :param producer_topic:
        :param consumer_topic:
        :param consumer_name:
        :param schema:
        """
        self.producer = Producer(client, producer_topic, schema=schema)
        self.consumer = Consumer(client, consumer_topic, consumer_name, schema=schema)

    def run(self, task, thread_count=None, _async=True, callback=None, logger=None):
        """
        多线程处理
        :param task: 任务程序
        :param thread_count: 指定最大线程数
        :param _async: 是否异步发送消息， True异步发送， Flase 同步发送
        :param callback: 异步发送的回调函数
        :param logger: 日志收集器
        :return:
        """
        def send_task(msg):
            result = task(msg)
            self.producer.send(result, _async, callback)
        self.consumer.receive(send_task, thread_count, logger)


class ProduceConsume(object):
    """发送数据至pulsar，订阅pulsar得到业务数据"""
    def __init__(self, client, producer_topic, consumer_topic, consumer_name, schema=pulsar.schema.StringSchema()):
        self.consumer = client.subscribe(consumer_topic, consumer_name, schema=schema)
        self.producer = client.create_producer(producer_topic, schema=schema)

    def run(self, data):
        self.producer.send(data)
        return self.consume()

    def consume(self):
        msg = self.consumer.receive()
        self.consumer.acknowledge(msg)
        return msg
