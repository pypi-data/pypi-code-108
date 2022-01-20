# -*- coding: UTF-8 -*-
# @Time : 2021/11/27 下午5:09 
# @Author : 刘洪波

import pulsar


def client(url: str):
    from pulsar_mq.Clients import Client
    return Client(url)


def create_consumer(clients, topics: list, consumer_name: str, schema=pulsar.schema.StringSchema()):
    from pulsar_mq.Consumers import Consumer
    return Consumer(clients, topics, consumer_name, schema)


def create_producer(clients, topic, schema):
    from pulsar_mq.Producers import Producer
    return Producer(clients, topic, schema)
