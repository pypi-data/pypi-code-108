import requests
from aishu import setting

class machine(object):
    def __init__(self, search):
        self.search = search

    def getAgentPort(self):
        if not (self.search):
            return False

        ip = setting.host
        headers = setting.header
        ports = []
        url = 'http://{ip}/etl/input/list?start=0&limit=-1&order=create_time&by=desc'.format(ip=ip)
        rsp = requests.get(url=url,headers=headers)
        inputList=rsp.json()

        for key in self.search:
            for input in inputList:
                if input['id'] == key:
                    ports.append(input['port'])
                    break

        if not (ports):
            return False

        if len(ports)==1:
            return str(ports[0])
        else:
            return ports
    def getIntPort(self):
        if not (self.search):
            return False

        ip = setting.host
        headers = setting.header
        ports = []
        url = 'http://{ip}/etl/input/list?start=0&limit=-1&order=create_time&by=desc'.format(ip=ip)
        rsp = requests.get(url=url,headers=headers)
        inputList=rsp.json()

        for key in self.search:
            for input in inputList:
                if input['id'] == key:
                    ports.append(input['port'])
                    break

        if not (ports):
            return False

        if len(ports)==1:
            return ports[0]
        else:
            return ports