'''
Author: 饕餮
Date: 2022-01-17 17:24:26
version: 
LastEditors: 饕餮
LastEditTime: 2022-01-20 09:32:27
Description: file content
'''
import requests
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

import json
from sangfor_af_sdk.Object.Auth import LoginResponseObject
from sangfor_af_sdk.Common.BaseRequest import BaseRequest
class SdkClient(object):
    def __init__(self,apiUser,apiPwd,apiAddr):
        self._apiUser = apiUser
        self._apiPwd = apiPwd
        self._apiAddr = apiAddr
        self._baseRequestHeaders = {
            "Connection":"keep-alive",
            "Content-Type":"application/json"
        }

    def _isJson(self,data):
        try:
            json_object = json.loads(data)
        except ValueError as e:
            return False
        return True

    def _isJsonStr(self,data):
        try:
            json_str = json.dumps(data)
        except ValueError as e:
            return False
        return True
    
    def _GetResponse(self,rUrl,rData,rType='GET'):
        rUrl = self._apiAddr + rUrl
        #发送亲求
        if rType == 'GET':
            responseData = requests.get(url=rUrl,params=rData,headers=self._baseRequestHeaders,verify=False)
        elif rType == 'POST':
            # json转字符串
            if self._isJsonStr(rData):
                rData = json.dumps(rData)
            responseData = requests.post(url=rUrl,data=rData,headers=self._baseRequestHeaders,verify=False)
        if responseData.status_code == 200:
            return json.loads(responseData.text)
        else:
            return None

    def GetToken(self):
        loginData = {
            "name":self._apiUser,
            "password":self._apiPwd
        }
        loginResponse = self._GetResponse('/namespaces/public/login',loginData,'POST')
        if loginResponse is not None:
            loginObject = LoginResponseObject(loginResponse)
            if loginObject.Code == 0:
                self._baseRequestHeaders["Cookie"] = "token={}".format(loginObject.Token)
                return True
            else:
                return False

    def GetResponse(self,request:BaseRequest):
        self.GetToken()
        responseData = self._GetResponse(request.requestUrl,request.requestData,request.requestType)
        if responseData is not None:
            return request.GetResponseObject(responseData)
        else:
            return None
        