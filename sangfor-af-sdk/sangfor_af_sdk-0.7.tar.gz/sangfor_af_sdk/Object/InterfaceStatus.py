'''
Author: 饕餮
Date: 2022-01-19 15:25:09
version: 
LastEditors: 饕餮
LastEditTime: 2022-01-20 09:49:03
Description: 接口状态信息
'''
from typing import List
from sangfor_af_sdk.Common.BaseObject import BaseObject
from sangfor_af_sdk.Common.BaseResponseObject import BaseResponseObejct

#接口统计信息
class Counter(BaseObject):
    def __init__(self,jsonData):
        self.ObjectData = jsonData

    @property
    def TxDropped(self):
        return self.TryGetValue("tx_dropped")

    @property
    def RxPackets(self):
        return self.TryGetValue("rx_packets")

    @property
    def TxBytes(self):
        return self.TryGetValue("tx_bytes")

    @property
    def TxPackets(self):
        return self.TryGetValue("tx_packets")

    @property
    def RxDropped(self):
        return self.TryGetValue("rx_dropped")

    @property
    def RxBytes(self):
        return self.TryGetValue("rx_bytes")

#接口吞吐率
class Speed(BaseObject):
    def __init__(self,jsonData):
        self.ObjectData = jsonData

    @property
    def Send(self):
        return self.TryGetValue("send")

    @property
    def Recv(self):
        return self.TryGetValue("recv")

#接口包收发速率
class BagSpeed(BaseObject):
    def __init__(self,jsonData):
        self.ObjectData = jsonData

    @property
    def Sendbag(self):
        return self.TryGetValue("sendbag")

    @property
    def Recvbag(self):
        return self.TryGetValue("recvbag")

#接口信息
class Information(BaseObject):
    def __init__(self,jsonData):
        self.ObjectData = jsonData

    @property
    def Duplex(self):
        return self.TryGetValue("duplex")

    @property
    def Duplexspeed(self):
        return self.TryGetValue("duplexSpeed")

    @property
    def Bagspeed(self) -> BagSpeed:
        tmpData = self.TryGetValue("bagSpeed")
        tmpObject = BagSpeed(tmpData)
        return tmpObject

    @property
    def Connectstatus(self):
        return self.TryGetValue("connectStatus")

    @property
    def Speed(self) -> Speed:
        tmpData = self.TryGetValue("speed")
        tmpObject = Speed(tmpData)
        return tmpObject

    @property
    def Supportedports(self):
        return self.TryGetValue("supportedPorts")

    @property
    def Counter(self) -> Counter:
        tmpData = self.TryGetValue("counter")
        tmpObject = Counter(tmpData)
        return tmpObject

class InterfaceStatus(BaseObject):
    def __init__(self,jsonData):
        self.ObjectData = jsonData

    @property
    def Interfacename(self):
        return self.TryGetValue("interfaceName")

    @property
    def Information(self):
        tmpData = self.TryGetValue("information")
        tmpObject = Information(tmpData)
        return tmpObject

class InterfaceStatusList(BaseResponseObejct):

    @property
    def StatusList(self) -> List[InterfaceStatus]:
        tmpDataList = self.BaseData
        returnList = []
        for interface in tmpDataList:
            returnList.append(InterfaceStatus(interface))
        return returnList