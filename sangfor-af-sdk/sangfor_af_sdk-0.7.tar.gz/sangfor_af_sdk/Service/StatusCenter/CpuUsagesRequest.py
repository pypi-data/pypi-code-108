'''
Author: 饕餮
Date: 2022-01-20 09:34:50
version: 
LastEditors: 饕餮
LastEditTime: 2022-01-20 10:38:06
Description: 获取cpu使用率变化曲线数据
'''
from sangfor_af_sdk.Common.BaseRequest import BaseRequest
from sangfor_af_sdk.Object.CpuUsages import CpuUsages


class CpuUsagesRequest(BaseRequest):
    def __init__(self):
        super().__init__("/namespaces/public/cpuusages", "GET")

    @property
    def TimeFilter(self):
        return self.TryGetValue("timeFilter")

    @TimeFilter.setter
    def TimeFilter(self,value):
        self.SetValue("timeFilter",value)

    def GetResponseObject(self, responseData):
        cpuUsagesList = CpuUsages(responseData)
        return cpuUsagesList