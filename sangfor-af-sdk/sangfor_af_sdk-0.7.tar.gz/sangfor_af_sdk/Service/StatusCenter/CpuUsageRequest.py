'''
Author: 饕餮
Date: 2022-01-20 10:35:23
version: 
LastEditors: 饕餮
LastEditTime: 2022-01-20 10:44:23
Description: file content
'''
from sangfor_af_sdk.Common.BaseRequest import BaseRequest
from sangfor_af_sdk.Object.CpuUsage import CpuUsage

class MemoryUsageRequest(BaseRequest):
    def __init__(self):
        super().__init__("/namespaces/public/cpuusage", "GET")

    def GetResponseObject(self, responseData):
        memoryUsageObject = CpuUsage(responseData)
        return memoryUsageObject