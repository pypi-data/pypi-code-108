# -*- coding: UTF-8 -*-
import sys
from nn_sdk.engine_csdk import sdk_new,sdk_delete,sdk_process,sdk_init,sdk_uninit,sdk_version

__all__ = ['csdk_object']

# c库 参考 nn_sdk.h
# java 参考 nn_sdk.java
class csdk_object:
    def __init__(self,conf):
        self._instance = None
        sdk_init()
        self._instance = sdk_new(conf)
        print("csdk_object create ", self._instance)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb is None:
            self.close()
        else:
            print("[Exit %s]: Exited with exception raised." % self._instance)

    @property
    def instance(self):
        return self._instance

    def valid(self):
        return self._instance is not None and self._instance > 0

    def close(self):
        if self._instance is not None and self._instance > 0:
            print('csdk_object destroy',self._instance)
            code = sdk_delete(self._instance)
            self._instance = 0
    '''
        stage 子图id(0,1,...)
        input 为该子图的输入,支持多输入。
    '''
    def process(self,stage:int,*input):
        code, result = sdk_process(self._instance,stage, *input)
        return code,result