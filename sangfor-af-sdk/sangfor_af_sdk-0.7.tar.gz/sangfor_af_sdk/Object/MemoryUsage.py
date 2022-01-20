'''
Author: 饕餮
Date: 2022-01-20 10:17:43
version: 
LastEditors: 饕餮
LastEditTime: 2022-01-20 10:30:24
Description: 内存使用率
'''
from sangfor_af_sdk.Common.BaseResponseObject import BaseResponseObejct

class MemoryUsage(BaseResponseObejct):

    @property
    def Usage(self):
        return self.TryGetValue("data.memoryUsage")