# -*- coding: UTF-8 -*-
# @Time : 2021/12/1 下午4:04 
# @Author : 刘洪波

from concurrent.futures import ThreadPoolExecutor

"""
pulsar服务
1. 订阅pulsar
2. 处理消费的数据
3. 发送得到的结果
"""


class Service(object):
    def __init__(self, client, producer_topic: str, consumer_topic: str, consumer_name: str, schema):
        """
        创建 生产者 和 消费者
        :param client:
        :param producer_topic:
        :param consumer_topic:
        :param consumer_name:
        :param schema:
        """
        self.producer = client.create_producer(producer_topic, schema=schema)
        self.consumer = client.subscribe(consumer_topic, consumer_name, schema=schema)

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
        if thread_count:
            pool = ThreadPoolExecutor(max_workers=thread_count)
            while True:
                msg = self.consumer.receive()
                pool.submit(self.acknowledge, task, msg, _async, callback, logger)
        else:
            while True:
                msg = self.consumer.receive()
                self.acknowledge(task, msg, _async, callback, logger)

    def acknowledge(self, task, msg, _async, callback, logger):
        try:
            if logger:
                result = task(msg, logger)
            else:
                result = task(msg)
            if result:
                if _async:
                    self.producer.send_async(result, callback=callback)
                else:
                    self.producer.send(result)
            self.consumer.acknowledge(msg)
        except Exception as e:
            # 消息未被成功处理
            self.consumer.acknowledge(msg)
            if logger:
                logger.error('运行异常，报错信息如下：')
                logger.error(e)
            else:
                print('运行异常，报错信息如下：')
                print(e)
            raise e
