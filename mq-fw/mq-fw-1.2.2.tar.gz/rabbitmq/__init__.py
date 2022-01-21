# -*- coding: UTF-8 -*-
# @Time : 2021/12/2 下午5:54 
# @Author : 刘洪波


def connect(host, port, username, password):
    from rabbitmq.Connections import Connection
    return Connection(host, port, username, password)
