#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 23:57:12 2022

@author: Mohammad Asim
"""

import tensorflow as tf

class Input():
    
    def __init__(self, config, data_type='tfrecord', split=0, shuffle=False, shuffle_buffer=1024, thresh=800, normalize=True):
        self.train_dataset = config['train']
        self.validation_dataset = config['validation']
        self.train_batch_size = None
        self.data_type = data_type
        self.split = split
        self.shuffle = shuffle
        self.window_length = 16
        self.thresh = thresh
        self.normalize=normalize
        self.shuffle_buffer = shuffle_buffer
        self.config = config
        self.width = len(config['input_feature'])
        self.dataset()
        
    def dataset(self):
        print(self.train_dataset)
        if(type(self.train_dataset) in [list, tuple]):
            if(self.data_type=='tfrecord'):
                self.train_dataset = tf.data.TFRecordDataset(self.train_dataset, num_parallel_reads=tf.data.AUTOTUNE)
        else:
            raise TypeError("Only list, tuple are allowed")
            
        if(type(self.validation_dataset) in [list, tuple]):
            if(self.data_type=='tfrecord'):
                self.validation_dataset = tf.data.TFRecordDataset(self.validation_dataset, num_parallel_reads=tf.data.AUTOTUNE)
            
        elif(self.val_data is not None):
            raise TypeError("Only list, tuple are allowed")
            
    def build(self, train_batch_size=32, validation_batch_size=32):
        self.train_batch_size = train_batch_size
        self.validation_batch_size = validation_batch_size
        if(self.train_dataset is not None):
            if(self.data_type=='tfrecord'):
                self.train_dataset = self.train_dataset.map(self._parse_tf_record, num_parallel_calls=tf.data.AUTOTUNE)
            if(self.shuffle):
                self.train_dataset = self.train_dataset.shuffle(self.shuffle_buffer)
            self.train_dataset = self.train_dataset.batch(self.train_batch_size*self.window_length, drop_remainder=True)
            self.train_dataset = self.train_dataset.map(self._reshape_train, num_parallel_calls=tf.data.AUTOTUNE)
            self.train_dataset = self.train_dataset.cache()
            self.train_dataset = self.train_dataset.prefetch(tf.data.AUTOTUNE)
        if(self.validation_dataset is not None):
            if(self.data_type=='tfrecord'):
                self.validation_dataset = self.validation_dataset.map(self._parse_tf_record, num_parallel_calls=tf.data.AUTOTUNE)
            if(self.shuffle):
                self.validation_dataset = self.validation_dataset.shuffle(self.shuffle_buffer)
            self.validation_dataset = self.validation_dataset.batch(self.validation_batch_size*self.window_length, drop_remainder=True)
            self.validation_dataset = self.validation_dataset.map(self._reshape_validation, num_parallel_calls=tf.data.AUTOTUNE)
            self.validation_dataset = self.validation_dataset.cache()
            self.validation_dataset = self.validation_dataset.prefetch(tf.data.AUTOTUNE)
        return self
    
    def _parse_tf_record(self, inp):
        features = {
            "timestamp": tf.io.FixedLenFeature([], tf.string), 
            "mains": tf.io.FixedLenFeature([], tf.float32),
            "diff": tf.io.FixedLenFeature([], tf.float32)
        }
        for name in self.config['input_feature']:
            features[name] = tf.io.FixedLenFeature([], tf.float32)
        data = tf.io.parse_single_example(inp, features)
        if(self.normalize):
            return [data['mains']/self.thresh, data['diff']/self.thresh],data[self.config['input_feature'][0]]/self.thresh
        else:
            return [data['mains'], data['diff']],data['fridge']
    
    def _reshape_train(self, mains, appliance):
        return tf.reshape(mains, [self.train_batch_size, self.window_length, 2]), tf.reshape(appliance, [self.train_batch_size, self.window_length, 1])
    
    def _reshape_validation(self, mains, appliance):
        return tf.reshape(mains, [self.validation_batch_size, self.window_length, 2]), tf.reshape(appliance, [self.validation_batch_size, self.window_length, 1])
