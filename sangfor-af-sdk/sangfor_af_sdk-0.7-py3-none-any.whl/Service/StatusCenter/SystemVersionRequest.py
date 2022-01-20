'''
Author: 饕餮
Date: 2022-01-19 17:38:40
version: 
LastEditors: 饕餮
LastEditTime: 2022-01-19 18:15:44
Description: 获取系统版本信息
'''
from sangfor_af_sdk.Common.BaseRequest import BaseRequest
from sangfor_af_sdk.Object.SystemVersion import SystemVersion
class SystemVersionRequest(BaseRequest):
    def __init__(self):
        super().__init__("/namespaces/public/systemversion", "GET")

    @property
    def Filter(self):
        self.TryGetValue("filter")

    @Filter.setter
    def Filter(self,value):
        self.SetValue("filter",value)

    def GetResponseObject(self, responseData):
        systemVersionObject = SystemVersion(responseData)
        return systemVersionObject