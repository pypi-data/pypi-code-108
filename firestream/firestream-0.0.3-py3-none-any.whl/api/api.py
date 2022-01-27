#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 23:50:25 2022

@author: admin
"""
from firestream.stream import Input
from firestream.model import Disaggregator
class Api():
    
    def __init__(self, config):
        self.config = config
        self.models = config['models'] if 'models' in config.keys() else None
        self.appliances = config['appliances']
        self.optimizers = config['optimizers']
        
    def start(self):
        for appliance in self.appliances:
            print('Training for appliance: ', appliance)
            print('======================')
            self.config['appliance'] = appliance
            stream = Input(self.config)
            stream = stream.build()
            for obj in self.models:
                print('Model: ', obj['name'])
                print('------')
                for optimizer in self.optimizers:
                    print('Optimizer: ', optimizer)
                    print('++++++++++')
                    disaggregator = Disaggregator('WindowGRU', stream, obj['model'](stream))
                    disaggregator.train()