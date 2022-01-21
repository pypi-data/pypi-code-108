
# !/usr/bin/env python
# -*- coding: UTF-8 -*-
from aishu.datafaker.profession.entity import port
from aishu.public import urlJoin
import requests
import time
import json

class Port():
    def __init__(self):
        pass

    def httpport(self):
        url = '/etl/input'
        http_port = port.date().getEtlPortNew()
        body = {
            "community":[],
            "port":http_port,
            "agentProtocol":"HTTP",
            "protocol":"AR-Agent",
            "ruleName":None,
            "status":1,
            "type":None,
            "tagsID":[],
            "tags":[],
            "timezone":"Asia/Shanghai",
            "charset":"UTF-8"
        }
        requests.post(urlJoin.url(url), json.dumps(body))
        return http_port

    def syslogPort(self):
        url_syslog = '/etl/input'
        syslog_port = port.date().getEtlPortNew()
        body_syslog = {
            "community":[],
            "port": syslog_port,
            "protocol":"syslog",
            "ruleName":None,
            "status":1,
            "tagsID":[],
            "tags":[],
            "timezone":"Asia/Shanghai",
            "type":"syslog",
            "charset":"UTF-8"
        }
        requests.post(urlJoin.url(url_syslog), json.dumps(body_syslog))
        return syslog_port
