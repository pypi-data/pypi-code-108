'''
Author: 饕餮
Date: 2022-01-20 09:40:09
version: 
LastEditors: 饕餮
LastEditTime: 2022-01-20 10:29:33
Description: cpu使用率变化曲线数据
'''
from typing import List
from sangfor_af_sdk.Common.BaseResponseObject import BaseResponseObejct
from sangfor_af_sdk.Object.StatusCenterBase import Usage
    

class MemoryUsages(BaseResponseObejct):

    @property
    def UsagesList(self) -> List[Usage]:
        tmpData =  self.TryGetValue("data.memoryUsages")
        returnData = []
        for usage in tmpData:
            usageObject = Usage(usage)
            returnData.append(usageObject)
        return returnData