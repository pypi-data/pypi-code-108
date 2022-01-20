'''
Author: 饕餮
Date: 2022-01-19 13:48:00
version: 
LastEditors: 饕餮
LastEditTime: 2022-01-19 17:51:52
Description: file content
'''
from sangfor_af_sdk.Common.BaseRequest import BaseRequest
from sangfor_af_sdk.Object.InterfaceStatus import InterfaceStatusList
class InterfaceStatusRequest(BaseRequest):
    def __init__(self):
        super().__init__("/namespaces/public/interfacestatus/", "GET")

    @property
    def Interface(self):
        return self.requestUrl.split('/')[-1]

    @Interface.setter
    def Interface(self,value):
        urlQuery = self.requestUrl.split('/')
        urlQuery[-1] = value
        self.requestUrl = "/".join(urlQuery)

    def GetResponseObject(self, responseData):
        interfaceList = InterfaceStatusList(responseData)
        return interfaceList