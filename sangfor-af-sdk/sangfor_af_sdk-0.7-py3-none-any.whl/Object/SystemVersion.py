'''
Author: 饕餮
Date: 2022-01-19 17:46:13
version: 
LastEditors: 饕餮
LastEditTime: 2022-01-19 18:30:15
Description: 系统版本信息
'''
from sangfor_af_sdk.Common.BaseResponseObject import BaseResponseObejct


class SystemVersion(BaseResponseObejct):

    @property
    def En(self):
        return self.TryGetValue("data.EN")

    @property
    def Build(self):
        return self.TryGetValue("data.build")

    @property
    def R(self):
        return self.TryGetValue("data.R")

    @property
    def Full(self):
        return self.TryGetValue("data.full")

    @property
    def Hf(self):
        return self.TryGetValue("data.HF")

    @property
    def Major(self):
        return self.TryGetValue("data.major")

    @property
    def Increase(self):
        return self.TryGetValue("data.increase")

    @property
    def B(self):
        return self.TryGetValue("data.B")

    @property
    def Addinfo(self):
        return self.TryGetValue("data.addInfo")

    @property
    def Minor(self):
        return self.TryGetValue("data.minor")