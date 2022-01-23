from sdsRayanArvin.Dataset import DeviceData
from sdsRayanArvin.Repository import Repository


class Data(Repository):
    def LastDataOnTopic(self, topic, type_data, pan, add):
        try:
            res = self.Request.sendWithToken('GET', 'device-data/' + topic + '/' + type_data + '/' + pan + '/' + add)
            return DeviceData(res['success'])
        except:
            return None

    def StoreDataOnTopic(self, data):
        res = self.Request.sendWithToken('POST', 'data', data)
        return res

