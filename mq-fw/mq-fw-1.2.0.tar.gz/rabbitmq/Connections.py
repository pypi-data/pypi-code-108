# -*- coding: UTF-8 -*-
# @Time : 2021/12/2 下午5:55 
# @Author : 刘洪波
import pika
from concurrent.futures import ThreadPoolExecutor


class Connection(object):
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.queue_name = None

    def create_queue(self, exchange, routing_key, durable=False):
        """
        创建 消息队列
        :param exchange:
        :param routing_key:
        :param durable:
        :return:
        """
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=self.host, port=self.port, credentials=pika.PlainCredentials(self.username, self.password))
        )
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange, exchange_type='topic', durable=durable)
        result = channel.queue_declare(queue='')
        self.queue_name = result.method.queue
        channel.queue_bind(exchange=exchange, queue=self.queue_name, routing_key=routing_key)
        connection.close()

    def consumer(self, task):
        """
        消费者
        :param task:  处理消息的业务功能
        :return:
        """
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=self.host, port=self.port, credentials=pika.PlainCredentials(self.username, self.password))
        )
        channel = connection.channel()

        def callback(ch, method, properties, body):
            body = body.decode('utf8')
            task(body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        channel.basic_consume(queue=self.queue_name, auto_ack=False, on_message_callback=callback)
        channel.basic_qos(prefetch_count=1)
        channel.start_consuming()

    def send(self, message_list: list, exchange, routing_key, durable=False):
        """
        发送数据
        :param message_list:
        :param exchange:
        :param routing_key:
        :param durable:
        :return:
        """
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=self.host, port=self.port, credentials=pika.PlainCredentials(self.username, self.password))
        )
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange, exchange_type='topic', durable=durable)
        for message in message_list:
            channel.basic_publish(exchange=exchange, routing_key=routing_key, body=message)
        connection.close()

    def receive(self, exchange, routing_key, task, durable=False, thread_count=None):
        """
        消费者消费
        :param exchange:
        :param routing_key:
        :param task:
        :param durable:
        :param thread_count: 当thread_count 有值的时候，可以进行多线程并行消费
        :return:
        """
        self.create_queue(exchange, routing_key, durable)
        if thread_count:
            pool = ThreadPoolExecutor(max_workers=thread_count)
            for i in range(thread_count):
                pool.submit(self.consumer, task)
        else:
            self.consumer(task)

    def service(self, task, consumer_exchange, consumer_routing_key,
                producer_exchange, producer_routing_key, durable=False, thread_count=None):
        """
        rabbitmq 服务
        1. 订阅rabbitmq
        2. 处理消费的数据
        3. 发送得到的结果
        :param task:
        :param consumer_exchange:
        :param consumer_routing_key:
        :param producer_exchange:
        :param producer_routing_key:
        :param thread_count:
        :param durable:
        :return:
        """
        def callback(body):
            result = task(body)
            if result:
                self.send(result, producer_exchange, producer_routing_key, durable)
        self.receive(consumer_exchange, consumer_routing_key, callback, durable, thread_count)

