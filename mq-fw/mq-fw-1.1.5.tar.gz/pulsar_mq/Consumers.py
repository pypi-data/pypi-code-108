# -*- coding: UTF-8 -*-
# @Time : 2021/11/27 下午5:36 
# @Author : 刘洪波

from concurrent.futures import ThreadPoolExecutor


class Consumer(object):
    def __init__(self, client, topic, consumer_name, schema):
        self.consumer = client.subscribe(topic, consumer_name, schema=schema)

    def receive(self, task, thread_count=None, logger=None):
        """
        :param task: 任务程序
        :param thread_count: 指定最大线程数
        :param logger: 日志收集器
        :return:
        """
        if thread_count:
            """多线程处理"""
            pool = ThreadPoolExecutor(max_workers=thread_count)
            while True:
                msg = self.consumer.receive()
                pool.submit(self.acknowledge, task, msg, logger)
        else:
            """消费一个，处理一个"""
            while True:
                msg = self.consumer.receive()
                self.acknowledge(task, msg, logger)

    def acknowledge(self, task, msg, logger):
        try:
            task(msg)
            self.consumer.acknowledge(msg)
        except Exception as e:
            # 消息未被成功处理
            self.consumer.acknowledge(msg)
            if logger:
                logger.error('消费异常，报错信息如下：')
                logger.error(e)
            else:
                print('消费异常，报错信息如下：')
                print(e)
            raise e
