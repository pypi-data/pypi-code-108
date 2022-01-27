#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 23:59:01 2022

@author: Mohammad Asim
"""

from tensorflow.keras import Model
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv1D, GRU, Bidirectional, Dropout
class WindowGRU(Model):
    
    def __init__(self, name, stream, model=None):
        super(WindowGRU, self).__init__()
        self.model = model
        self.stream = stream
        self.conv1d_0 = Conv1D(16, 4, activation='relu', input_shape=(self.stream.window_length,2), padding="same", strides=1)
        self.bidirectional_gru_0 = Bidirectional(GRU(64, activation='relu', return_sequences=True), merge_mode='concat')
        self.dropout_0 = Dropout(0.5)
        self.bidirectional_gru_1 = Bidirectional(GRU(128, activation='relu', return_sequences=False), merge_mode='concat')
        self.dropout_1 = Dropout(0.5)
        self.dense_0 = Dense(128, activation='relu')
        self.dropout_1 = Dropout(0.5)
        self.dense_1 = Dense(1, activation='linear')
        self.build((None, self.stream.window_length, 2))

    def call(self, inputs, training=False):
        x = self.conv1d_0(inputs)
        x = self.bidirectional_gru_0(x)
        x = self.dropout_0(x)
        x = self.bidirectional_gru_1(x)
        x = self.dropout_1(x)
        x = self.dense_0(x)
        x = self.dropout_1(x)
        return self.dense_1(x)

    def train(self, epochs=5, loss='mse', optimizer='adam'):
        self.compile(loss=loss, optimizer=optimizer)
        return self.fit(self.stream.train_dataset, validation_data=self.stream.validation_dataset, epochs=epochs)
