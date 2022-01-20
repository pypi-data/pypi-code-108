'''
Author: 饕餮
Date: 2022-01-17 16:49:10
version: 
LastEditors: 饕餮
LastEditTime: 2022-01-19 17:59:01
Description: file content
'''

class BaseRequest:
    def __init__(self,rUrl,rType):
        self.requestUrl = rUrl
        self.requestType = rType
        self.requestData = {}

    def get_request_data(self):
        return self.requestData

    def set_request_data(self,value):
        self.requestData = value

    def TryGetValue(self,key,default=None):
        keyArray = key.split('.')
        keyStr = ""
        #key内容为字典的不存在则返回默认
        if len(keyArray) > 0:
            baseDic = self.requestData
            for k in keyArray[0:len(keyArray)]:
                if k not in baseDic.keys():
                    return default
                baseDic = baseDic[k]
        #key栈组装
        for k in keyArray:
            keyStr +="['{0}']".format(k)
        #数据赋值
        return eval("self.requestData" + keyStr)

    def SetValue(self,key,value):
        keyArray = key.split('.')
        keyStr = ""
        #key内容为字典的不存在则建立
        if len(keyArray) > 1:
            baseDic = self.requestData
            for k in keyArray[0:len(keyArray)-1]:
                if k not in baseDic.keys():
                    baseDic[k] = {}
                baseDic = baseDic[k]
        #key栈组装
        for k in keyArray:
            keyStr +="['{0}']".format(k)
        #数据赋值
        exec("self.requestData" + keyStr + "=value")

    def GetResponseObject(self,responseData):
        return responseData