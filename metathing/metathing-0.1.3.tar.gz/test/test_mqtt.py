#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from pdb import set_trace as stop
from metathing.metathing import MetaThing as MT
import random
import threading


class SampleApp():
    def __init__(self):
        self.__x = 10
        self.__y = 20
        self.ecbs = {}

    def initialize(self):
        print("App init")

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, x):
        self.__x = x

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, y):
        self.__y = y

    def Multiply(self, x, y):
        return x*y

    def Divide(self, x, y):
        return x/y

    # Event
    def CB_Generator(self):
        print("Generator called")
        if 'Generator' in self.ecbs:
            result = random.randint(0,100)
            self.ecbs['Generator'](result)

if __name__ == "__main__":
    config = {
        "ADDR": "0.0.0.0",
        "PORT": 10100,
        "WORKDIR": ".",
        "MQTT_ADDR": "localhost",
        "MQTT_PORT": 1883
    }
    srv_name = "test"
    mt = MT(config, srv_name)
    app = SampleApp()
    mt.Bind(app)
    t1 = threading.Timer(5, app.CB_Generator)
    t1.start()
    mt.Run()
    