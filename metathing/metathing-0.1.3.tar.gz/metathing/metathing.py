#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from metathing.service import Service

class MetaThing():
    def __init__(self, config: object, srv_name: str):
        self.srv = Service(config, srv_name)

    def Bind(self, app:object):
        self.srv.mqtt.connect()
        self.srv.Bind(app)
        self.srv.InitAllDevs()

    def Run(self):
        self.srv.http.Run()