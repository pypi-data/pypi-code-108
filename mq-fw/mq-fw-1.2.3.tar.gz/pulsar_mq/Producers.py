# -*- coding: UTF-8 -*-
# @Time : 2021/11/27 下午6:15 
# @Author : 刘洪波


class Producer(object):
    def __init__(self, client, topic, schema):
        self.producer = client.create_producer(topic, schema=schema)

    def send(self, msg, _async=True, callback=None):
        """
        发送消息
        :param msg: 需要发送的消息
        :param _async: 是否异步发送消息， True异步发送， Flase 同步发送
        :param callback: 异步发送时的回调函数
        :return:
        """
        if _async:
            if isinstance(msg, list):
                if len(msg) > 0:
                    for m in msg:
                        if len(m) > 0:
                            self.producer.send_async(m, callback=callback)
                else:
                    raise ValueError('No data to send, the list type is Empty')
            elif isinstance(msg, str):
                if len(msg) > 0:
                    self.producer.send_async(msg, callback=callback)
                else:
                    raise ValueError('No data to send, the str type is Empty')
            else:
                raise ValueError('the data type sent is wrong, the required type is list or str')
        else:
            if isinstance(msg, list):
                if len(msg) > 0:
                    for m in msg:
                        if len(m) > 0:
                            self.producer.send(m)
                else:
                    raise ValueError('No data to send, the list type is Empty')
            elif isinstance(msg, str):
                if len(msg) > 0:
                    self.producer.send(msg)
                else:
                    raise ValueError('No data to send, the str type is Empty')
            else:
                raise ValueError('the data type sent is wrong, the required type is list or str')
