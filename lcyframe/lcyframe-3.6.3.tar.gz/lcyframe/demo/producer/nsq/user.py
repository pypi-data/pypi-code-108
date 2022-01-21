#!/usr/bin/env python
# -*- coding:utf-8 -*-
from lcyframe import WriteNsq

class NsqEvent(WriteNsq):
    topic = "test"
    __events__ = ("on_create_user", )

