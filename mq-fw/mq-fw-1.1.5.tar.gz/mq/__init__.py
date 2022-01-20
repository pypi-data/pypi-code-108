# -*- coding: UTF-8 -*-
# @Time : 2021/12/3 下午6:36 
# @Author : 刘洪波


def rabbitmq_pulsar(host, port, username, password, url):
    from mq.Rabbitmq_pulsar import Interconnect
    return Interconnect(host, port, username, password, url)