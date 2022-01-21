import random
import requests
from aishu.public import urlJoin
from aishu.public.operationJson import OperetionJson
from aishu.setting import header


class date(object):
    def getPort(self):
        # 系统合法参数 20010-20099、162，514，5140
        portList = [port for port in range(20010, 20100)]
        portList.append(162)
        portList.append(514)
        portList.append(5140)
        port = random.choice(portList)
        return port

    def getEtlPort(self):
        path = "/etl/input/list?start=0&limit=-1"
        payload = {}
        headers = header
        response = requests.request("GET", urlJoin.url(path), headers=headers, data=payload)
        date = response.json()
        a = OperetionJson(date)
        value = a.get_value('port')
        if value:
            return value
        else:
            return []

    def getEtlPortOld(self):
        date = self.getEtlPort()
        if len(date) == 0:
            port = 0
            return port
        else:
            port = random.choice(date)
            return port

    def getEtlPortNew(self):
        oldNew = self.getEtlPort()
        count = 0
        flag = True
        while flag or count >= 10:
            newPort = self.getPort()
            count = count + 1
            if newPort not in oldNew:
                flag = False
                return newPort
        return ''

    def getEtlPortIll(self):
        portList = [port for port in range(10000, 20000)]
        port = random.choice(portList)
        return port
