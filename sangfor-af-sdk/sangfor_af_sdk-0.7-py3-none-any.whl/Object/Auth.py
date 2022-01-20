'''
Author: 饕餮
Date: 2022-01-17 17:42:26
version: 
LastEditors: 饕餮
LastEditTime: 2022-01-17 17:59:45
Description: file content
'''
from sangfor_af_sdk.Common.BaseResponseObject import BaseResponseObejct

class LoginResponseObject(BaseResponseObejct):
    def __init__(self, jsonData):
        super().__init__(jsonData)

    @property
    def Token(self):
        return self.TryGetValue("data.loginResult.token")

    @property
    def Name(self):
        return self.TryGetValue("data.name")

    @property
    def PasswdStatus(self):
        return self.TryGetValue("data.passwdStatus")

    @property
    def Role(self):
        return self.TryGetValue("data.role")

class LogoutResponseObject(BaseResponseObejct):
    def __init__(self, jsonData):
        super().__init__(jsonData)

    @property
    def Name(self):
        return self.TryGetValue("data.name")

class KeepAliveResponseObject(BaseResponseObejct):
    def __init__(self, jsonData):
        super().__init__(jsonData)

    @property
    def IsSuccess(self):
        tmpData = self.BaseData
        if tmpData == 0:
            return True
        else:
            return False
    
