'''
Author: 饕餮
Date: 2022-01-20 10:39:08
version: 
LastEditors: 饕餮
LastEditTime: 2022-01-20 10:41:20
Description: 设备运行时间
'''
from sangfor_af_sdk.Common.BaseResponseObject import BaseResponseObejct

class Uptimes(BaseResponseObejct):

    @property
    def Uptimes(self):
        return self.TryGetValue("data.upTimes")