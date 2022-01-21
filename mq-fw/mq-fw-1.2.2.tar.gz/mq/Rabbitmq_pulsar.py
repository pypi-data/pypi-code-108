# -*- coding: UTF-8 -*-
# @Time : 2021/12/3 下午7:05 
# @Author : 刘洪波
import pulsar_mq
import rabbitmq
from concurrent.futures import ThreadPoolExecutor

"""rabbitmq 和 pulsar互相通信"""


class Interconnect(object):
    def __init__(self, rabbitmq_host, rabbitmq_port, rabbitmq_username, rabbitmq_password, pulsar_url):
        """
        rabbitmq 和 pulsar 连接
        :param rabbitmq_host: rabbitmq 的 host
        :param rabbitmq_port: rabbitmq 的 port
        :param rabbitmq_username: rabbitmq 的 username
        :param rabbitmq_password: rabbitmq 的 password
        :param pulsar_url: pulsar的url
        """
        self.rabbitmq_connect = rabbitmq.connect(rabbitmq_host, rabbitmq_port, rabbitmq_username, rabbitmq_password)
        self.client = pulsar_mq.client(pulsar_url)

    def rabbitmq_to_pulsar(self, task, pulsar_topic, rabbitmq_exchange, rabbitmq_routing_key, durable=False,
                           rabbitmq_thread_count=None, _async=True, send_callback=None, logger=None):
        """
        1. 订阅rabbitmq
        2. 处理消费的数据
        3. 将处理后的数据 发送到 pulsar
        :param task:  该函数是处理消费的数据
        :param pulsar_topic:
        :param rabbitmq_exchange:
        :param rabbitmq_routing_key:
        :param durable:
        :param rabbitmq_thread_count:
        :param _async:  pulsar是否异步发送
        :param send_callback: pulsar异步发送时的回调函数
        :param logger: 日志收集器
        :return:
        """
        try:
            producer = self.client.create_producer(pulsar_topic)

            def callback(msg):
                result = task(msg)
                if result:
                    producer.send(result, _async, send_callback)

            self.rabbitmq_connect.receive(rabbitmq_exchange, rabbitmq_routing_key, callback,
                                          durable, rabbitmq_thread_count)
        except Exception as e:
            if logger:
                logger.error(e)
            else:
                print(e)

    def pulsar_to_rabbitmq(self, task, pulsar_topic, pulsar_consumer_name, rabbitmq_exchange, rabbitmq_routing_key,
                           durable=False, pulsar_thread_count=None, logger=None):
        """
        1. 订阅 pulsar
        2. 处理消费的数据
        3. 将处理后的数据发送到 rabbitmq
        :param task:
        :param pulsar_topic:
        :param pulsar_consumer_name:
        :param rabbitmq_exchange:
        :param rabbitmq_routing_key:
        :param pulsar_thread_count:
        :param durable:
        :param logger:
        :return:
        """
        try:
            consumer = self.client.create_consumer(pulsar_topic, pulsar_consumer_name)

            def callback(msg):
                result = task(msg)
                if result:
                    self.rabbitmq_connect.send(result, rabbitmq_exchange, rabbitmq_routing_key, durable)

            consumer.receive(callback, pulsar_thread_count, logger)
        except Exception as e:
            if logger:
                logger.error(e)
            else:
                print(e)

    def run(self, pulsar_producer_topic, pulsar_consumer_topic, pulsar_consumer_name,
            rabbitmq_send_exchange, rabbitmq_send_routing_key, rabbitmq_consumer_exchange,
            rabbitmq_consumer_routing_key, send_task=None, consumer_task=None, durable=False,
            consumer_durable=None, producer_durable=None,
            _async=True, send_callback=None, rabbitmq_thread_count=None, pulsar_thread_count=None,
            logger=None):
        """
        从 rabbitmq 订阅，将数据发送至 pulsar;
        并且从 pulsar 订阅，将数据发送至 rabbitmq
        :param send_task:
        :param consumer_task:
        :param pulsar_producer_topic:
        :param pulsar_consumer_topic:
        :param pulsar_consumer_name:
        :param rabbitmq_send_exchange:
        :param rabbitmq_send_routing_key:
        :param rabbitmq_consumer_exchange:
        :param rabbitmq_consumer_routing_key:
        :param durable:
        :param consumer_durable:
        :param producer_durable:
        :param _async:
        :param send_callback:
        :param rabbitmq_thread_count:
        :param pulsar_thread_count:
        :param logger:
        :return:
        """
        if logger:
            def send_task2(msg):
                logger.info('rabbitmq的输入：')
                logger.info(msg)
                return msg

            def consumer_task2(msg):
                logger.info('pulsar的输出：')
                logger.info(msg.data())
                return [msg.data()]
        else:
            def send_task2(msg): return msg

            def consumer_task2(msg): return [msg.data()]

        if send_task is None:
            send_task = send_task2
        if consumer_task is None:
            consumer_task = consumer_task2
        pool = ThreadPoolExecutor(max_workers=2)
        pool.submit(self.rabbitmq_to_pulsar, send_task, pulsar_producer_topic, rabbitmq_consumer_exchange,
                    rabbitmq_consumer_routing_key, durable=consumer_durable if consumer_durable else durable,
                    rabbitmq_thread_count=rabbitmq_thread_count,
                    _async=_async, send_callback=send_callback, logger=logger)
        pool.submit(self.pulsar_to_rabbitmq, consumer_task, pulsar_consumer_topic,
                    pulsar_consumer_name, rabbitmq_send_exchange, rabbitmq_send_routing_key,
                    durable=producer_durable if producer_durable else durable,
                    pulsar_thread_count=pulsar_thread_count, logger=logger)

