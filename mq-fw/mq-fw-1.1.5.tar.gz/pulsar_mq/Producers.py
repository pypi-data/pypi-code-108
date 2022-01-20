# -*- coding: UTF-8 -*-
# @Time : 2021/11/27 下午6:15 
# @Author : 刘洪波


class Producer(object):
    def __init__(self, client, topic, schema):
        self.producer = client.create_producer(topic, schema=schema)

    def send(self, msg, _async=True, callback=None, logger=None):
        """
        发送消息
        :param msg: 需要发送的消息
        :param _async: 是否异步发送消息， True异步发送， Flase 同步发送
        :param callback: 异步发送时的回调函数
        :param logger: 日志收集器
        :return:
        """
        try:
            if _async:
                self.producer.send_async(msg, callback=callback)
            else:
                self.producer.send(msg)
        except Exception as e:
            if logger:
                logger.error('生产异常，报错信息如下：')
                logger.error(e)
            else:
                print('生产异常，报错信息如下：')
                print(e)
            raise e
