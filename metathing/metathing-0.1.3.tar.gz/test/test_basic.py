#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from pdb import set_trace as stop
from metathing.metathing import MetaThing as MT

class SampleApp():
    def __init__(self):
        self.__x = 10
        self.__y = 20

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

if __name__ == "__main__":
    config = {
        "ADDR": "0.0.0.0",
        "PORT": 10100
    }
    srv_name = "test"
    mt = MT(config, srv_name)
    app = SampleApp()
    mt.Bind(app)
    mt.Run()
    