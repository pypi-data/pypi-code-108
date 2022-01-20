'''
Author: 饕餮
Date: 2022-01-20 10:27:08
version: 
LastEditors: 饕餮
LastEditTime: 2022-01-20 10:28:18
Description: 状态中心公共类
'''
from sangfor_af_sdk.Common.BaseObject import BaseObject

class Usage(BaseObject):
    def __init__(self,jsonData):
        self.ObjectData = jsonData

    @property
    def Usage(self):
        return self.TryGetValue("usage")

    @property
    def Time(self):
        return self.TryGetValue("time")