#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 23:59:01 2022

@author: Mohammad Asim
"""

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv1D, GRU, Bidirectional, Dropout
class Model():
    
    def __init__(self, name, stream, model=None):
        self.model = model
        self.stream = stream
        
    def build(self):
        if(self.model == None):
            self.model = Sequential()
            self.model.add(Conv1D(16,4,activation='relu',input_shape=(self.stream.window_length,2),padding="same",strides=1))
            self.model.add(Bidirectional(GRU(64, activation='relu', return_sequences=True), merge_mode='concat'))
            self.model.add(Dropout(0.5))
            self.model.add(Bidirectional(GRU(128, activation='relu', return_sequences=False), merge_mode='concat'))
            self.model.add(Dropout(0.5))
            self.model.add(Dense(128, activation='relu'))
            self.model.add(Dropout(0.5))
            self.model.add(Dense(1, activation='linear'))
            self.model.compile(loss='mse', optimizer='adam')
        return self       
     
    def train(self, epochs=200):
        self.history = self.model.fit(self.stream.train_dataset, validation_data=self.stream.validation_dataset, epochs=epochs)