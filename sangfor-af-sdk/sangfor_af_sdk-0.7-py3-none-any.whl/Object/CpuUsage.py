'''
Author: 饕餮
Date: 2022-01-20 10:31:53
version: 
LastEditors: 饕餮
LastEditTime: 2022-01-20 10:36:50
Description: cpu使用率
'''
from sangfor_af_sdk.Common.BaseResponseObject import BaseResponseObejct

class CpuUsage(BaseResponseObejct):

    @property
    def Cpu5minute(self):
        return self.TryGetValue("data.cpu5minute")

    @property
    def Cpu15minute(self):
        return self.TryGetValue("data.cpu15minute")

    @property
    def Cpu1minute(self):
        return self.TryGetValue("data.cpu1minute")

    @property
    def Cpuaverage(self):
        return self.TryGetValue("data.cpuAverage")

    @property
    def Cpudetail(self):
        return self.TryGetValue("data.cpuDetail")

    @property
    def Cpucurrent(self):
        return self.TryGetValue("data.cpuCurrent")