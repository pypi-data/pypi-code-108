#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 23:59:01 2022

@author: Mohammad Asim
"""

class Disaggregator():
    
    def __init__(self, name, stream, model):
        
        """
            Initialize disaggregator
        """
        
        self.model = model
        self.stream = stream
        self.history = []
    
    def train(self):

        """
            Function to starting training 
        """
        
        self.history = self.model.fit(self.stream.train_dataset, validation_data=self.stream.validation_dataset, epochs=self.stream.epochs)
