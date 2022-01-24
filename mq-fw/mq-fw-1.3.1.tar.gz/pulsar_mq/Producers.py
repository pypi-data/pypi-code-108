# -*- coding: UTF-8 -*-
# @Time : 2021/11/27 下午6:15 
# @Author : 刘洪波
import json


class Producer(object):
    def __init__(self, client, topic, schema):
        self.producer = client.create_producer(topic, schema=schema)

    def send(self, msg, _async=True, callback=None, random_topic=None):
        """
        发送消息
        :param msg: 需要发送的消息
        :param _async: 是否异步发送消息， True异步发送， Flase 同步发送
        :param callback: 异步发送时的回调函数
        :param random_topic: 是否有 随机topic
        :return:
        """
        if _async:
            if msg:
                if isinstance(msg, list):
                    if random_topic:
                        for m in msg:
                            if m:
                                m = dict(json.loads(m))
                                m['random_topic'] = random_topic
                                m = json.dumps(m)
                                self.producer.send_async(m, callback=callback)
                    else:
                        for m in msg:
                            if m:
                                self.producer.send_async(m, callback=callback)
                elif isinstance(msg, str):
                    if random_topic:
                        msg = dict(json.loads(msg))
                        msg['random_topic'] = random_topic
                        msg = json.dumps(msg)
                    self.producer.send_async(msg, callback=callback)
                else:
                    raise ValueError('the data type sent is wrong, the required type is list or str')
            else:
                raise ValueError('No data to send, the data is Empty')
        else:
            if msg:
                if isinstance(msg, list):
                    if random_topic:
                        for m in msg:
                            if m:
                                m = dict(json.loads(m))
                                m['random_topic'] = random_topic
                                m = json.dumps(m)
                                self.producer.send(m)
                    else:
                        for m in msg:
                            if m:
                                self.producer.send(m)
                elif isinstance(msg, str):
                    if random_topic:
                        msg = dict(json.loads(msg))
                        msg['random_topic'] = random_topic
                        msg = json.dumps(msg)
                    self.producer.send(msg)
                else:
                    raise ValueError('the data type sent is wrong, the required type is list or str')
            else:
                raise ValueError('No data to send, the data is Empty')

    def close(self):
        self.producer.close()
