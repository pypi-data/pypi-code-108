'''
Author: 饕餮
Date: 2022-01-20 10:08:05
version: 
LastEditors: 饕餮
LastEditTime: 2022-01-20 10:20:34
Description: 获取内存使用率
'''
from sangfor_af_sdk.Common.BaseRequest import BaseRequest
from sangfor_af_sdk.Object.MemoryUsage import MemoryUsage

class MemoryUsageRequest(BaseRequest):
    def __init__(self):
        super().__init__("/namespaces/public/memoryusage", "GET")

    def GetResponseObject(self, responseData):
        memoryUsageObject = MemoryUsage(responseData)
        return memoryUsageObject