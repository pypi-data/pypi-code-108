class DeviceData:
    def __init__(self, dataArray):
        self.__topic = dataArray['topic']
        self.__type = dataArray['type']
        self.__data = dataArray['data']
        self.__pan = dataArray['pan']
        self.__add = dataArray['add']
        self.__IdDeviceData = dataArray['ID_device_data']

    def getIdDeviceData(self):
        return self.__IdDeviceData

    def getType(self):
        return self.__type

    def getTopic(self):
        return self.__topic

    def getData(self):
        return self.__data

    def getPan(self):
        return self.__pan

    def getAdd(self):
        return self.__add
