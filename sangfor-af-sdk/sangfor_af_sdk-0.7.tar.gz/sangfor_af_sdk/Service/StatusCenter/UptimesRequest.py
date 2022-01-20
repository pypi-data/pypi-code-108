'''
Author: 饕餮
Date: 2022-01-20 10:42:44
version: 
LastEditors: 饕餮
LastEditTime: 2022-01-20 10:47:12
Description: 获取设备运行时间
'''
from sangfor_af_sdk.Common.BaseRequest import BaseRequest
from sangfor_af_sdk.Object.Uptimes import Uptimes

class MemoryUsageRequest(BaseRequest):
    def __init__(self):
        super().__init__("/namespaces/public/uptimes", "GET")

    def GetResponseObject(self, responseData):
        memoryUsageObject = Uptimes(responseData)
        return memoryUsageObject