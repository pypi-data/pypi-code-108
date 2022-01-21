#!/usr/bin/env python
# -*- coding:utf-8 -*-
from lcyframe import WriteMqtt

class MqttEvent(WriteMqtt):
    qos = 2
    topic = "topic1"
    __events__ = ("on_create_user", )

