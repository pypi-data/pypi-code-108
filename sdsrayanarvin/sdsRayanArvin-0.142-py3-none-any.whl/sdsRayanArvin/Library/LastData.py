from sdsRayanArvin.Dataset import DeviceData


class LastData:
    LastDataDevice = {}

    def setLastData(self, LastDataDevice):
        index = str(LastDataDevice['topic']) + str(LastDataDevice['type']) + str(LastDataDevice['pan']) + str(LastDataDevice['add'])
        LastDataDevice['ID_device_data'] = 0
        LastDataDevice['data'] = str(LastDataDevice['data'])
        LastData.LastDataDevice[index] = DeviceData(LastDataDevice)
        self.getLastData(index)

    def setLastDataDevices(self, LastDataDevice: DeviceData):
        if LastDataDevice is None:
            return
        
        index = str(LastDataDevice.getTopic()) + str(LastDataDevice.getType()) + str(LastDataDevice.getPan()) + str(LastDataDevice.getAdd())
        LastData.LastDataDevice[index] = LastDataDevice

    def getLastData(self, index):
        return LastData.LastDataDevice[index]
