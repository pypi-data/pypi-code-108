'''
Author: 饕餮
Date: 2022-01-17 17:36:13
version: 
LastEditors: 饕餮
LastEditTime: 2022-01-17 17:40:32
Description: file content
'''
from sangfor_af_sdk.Common.BaseObject import BaseObject
class BaseResponseObejct(BaseObject):
    def __init__(self,jsonData):
        self.ObjectData = jsonData

    @property
    def BaseData(self):
        return self.TryGetValue("data")

    @property
    def Code(self):
        return self.TryGetValue("code")

    @property
    def Message(self):
        return self.TryGetValue("message")
