from sdsRayanArvin.Library.LastData import LastData

from sdsRayanArvin.Dataset.AuxStationData import Aux
from sdsRayanArvin.RepositoryApi.DataApi import Data


class Pipeline:
    def GetLastData(self, Aux_data: Aux, deviceData: Data, localData=None):
        if Aux_data is None:
            return 0

        type_aux = None

        if Aux_data.type == 1:
            type_aux = 'DO'
        if Aux_data.type == 2:
            type_aux = 'DI'
        if Aux_data.type == 3:
            return self.ReplaceTagWithValue(Aux_data, deviceData, 'AI')  # AI
        if Aux_data.type == 5:
            type_aux = 'VDO'
        if Aux_data.type == 6:
            return self.ReplaceTagWithValue(Aux_data, deviceData, localData=localData)  # AII
        if Aux_data.type == 8:
            return self.SwitchTagMode(Aux_data, deviceData, localData=localData)

        if type_aux is None:
            return None

        # if localData is None:
        #     Last_data = deviceData.LastDataOnTopic(str(Aux_data.code),
        #                                            str(type_aux),
        #                                            str(Aux_data.pan),
        #                                            str(Aux_data.address))
        #     LastData().setLastDataDevices(Last_data)
        # else:
        #     index = str(Aux_data.code) + str(type_aux) + str(Aux_data.pan) + str(Aux_data.address)
        #     try:
        #         Last_data = localData[index]
        #     except:
        #         Last_data = deviceData.LastDataOnTopic(str(Aux_data.code),
        #                                                str(type_aux),
        #                                                str(Aux_data.pan),
        #                                                str(Aux_data.address))
        #         LastDeviceData = {
        #             'topic': Aux_data.code,
        #             'type': type_aux,
        #             'data': Last_data.getData(),
        #             'pan': Aux_data.pan,
        #             'add': Aux_data.address,
        #         }

        #         LastData().setLastData(LastDeviceData)
        #         Last_data = LastData().getLastData(index).getData()

        Last_data = deviceData.LastDataOnTopic(str(Aux_data.code),
                                                str(type_aux),
                                                str(Aux_data.pan),
                                                str(Aux_data.address))
        if Last_data is not None:
            if Aux_data.type == 1 or Aux_data.type == 2 or Aux_data.type == 5:
                try:
                    idxOutput = Aux_data.output - 1
                    binOutput = "{0:b}".format(int(Last_data.getData()))
                    binOutputArray = list(binOutput)
                    binOutputArray.reverse()
                    if len(binOutputArray) > idxOutput:
                        return binOutputArray[idxOutput]
                    else:
                        return 0
                except:
                    return 0

            return Last_data.getData()
        else:
            return None

    def SwitchTagMode(self, Aux_data: Aux, deviceData: Data, tag=None, localData=None):
        if tag is None:
            arrayMath = Aux_data.Analog.math.split(' ')
            mode = arrayMath[0]
            modeArray = mode.split('-')
            tagChecker = modeArray[0]
            if tagChecker == 'AVG' or tagChecker == 'SUM' or tagChecker == 'MAX' or tagChecker == 'MIN':
                # Remove tag and set deviceData
                arrayMath.pop(0)
                zigbeeArray = modeArray[1].split(',')
                arrayOfData = []
                for zigbee in zigbeeArray:
                    panAndAddress = zigbee.split('.')
                    pan = panAndAddress[0]
                    address = panAndAddress[1]
                    tag = arrayMath[0]
                    getLastData = float(self.ReplaceTagWithValue(Aux_data, deviceData, tag, localData, arrayMath, pan, address))
                    if getLastData > 0:
                        arrayOfData.append(getLastData)

                if tagChecker == 'AVG':
                    return round(sum(arrayOfData) / len(arrayOfData), 2)
                if tagChecker == 'SUM':
                    return round(sum(arrayOfData), 2)
                if tagChecker == 'MAX':
                    return round(max(arrayOfData), 2)
                if tagChecker == 'MIN':
                    return round(min(arrayOfData), 2)

                return None

        return self.ReplaceTagWithValue(Aux_data, deviceData, tag, localData)

    def ReplaceTagWithValue(self, Aux_data: Aux, deviceData: Data, tag=None, localData=None, arrayMath=None, pan=None, address=None):
        if arrayMath is None:
            arrayMath = Aux_data.Analog.math.split(' ')
        if tag is None:
            tag = arrayMath[0]

        code = str(Aux_data.code)
        if pan is None:
            pan = str(Aux_data.pan)
        if address is None:
            address = str(Aux_data.address)

        if tag == 'PERCENT':
            code = code + str(pan) + str(address) + str(arrayMath[1])

        # if localData is None or tag == 'PERCENT':
        #     Last_data = deviceData.LastDataOnTopic(str(code),
        #                                            str(tag),
        #                                            str(pan),
        #                                            str(address))
        #     LastData().setLastDataDevices(Last_data)
        # else:
        #     index = str(code) + str(tag) + str(pan) + str(address)
        #     try:
        #         Last_data = localData[index]
        #     except:
        #         Last_data = deviceData.LastDataOnTopic(str(code),
        #                                                str(tag),
        #                                                str(pan),
        #                                                str(address))
        #         LastDeviceData = {
        #             'topic': code,
        #             'type': tag,
        #             'data': Last_data.getData(),
        #             'pan': pan,
        #             'add': address,
        #         }
        #         LastData().setLastData(LastDeviceData)
        #         Last_data = LastData().getLastData(index)

        Last_data = deviceData.LastDataOnTopic(str(code),
                                                str(tag),
                                                str(pan),
                                                str(address))
                                                
        data = None if Last_data is None else Last_data.getData()

        if data is None:
            return None

        idxOutput = Aux_data.output - 1

        lastDataArray = data.split('/')

        if tag == 'PERCENT':
            return int(lastDataArray[2])

        if len(lastDataArray) > 1:
            data = lastDataArray[idxOutput]

        finalData = data

        if arrayMath is not None:
            finalData = ' '.join(arrayMath).replace(arrayMath[0], data)
            
        return  round(self.ReplaceMathWithValue(finalData), 2)

    def ReplaceMathWithValue(self, value):
        arrayMath = value.split(' ')

        if len(arrayMath) == 1:
            return arrayMath[0]

        value = 0

        for idx, val in enumerate(arrayMath):
            if idx == 0 or idx == len(arrayMath) - 1 or idx % 2 == 0:
                continue

            nextVal = float(arrayMath[idx + 1])
            preVal = float(arrayMath[idx - 1])

            if val == '+':
                if value == 0:
                    value = preVal + nextVal
                else:
                    value += nextVal

            if val == '-':
                if value == 0:
                    value = preVal - nextVal
                else:
                    value -= nextVal

            if val == '/':
                if value == 0:
                    value = preVal / nextVal
                else:
                    value /= nextVal

            if val == '*':
                if value == 0:
                    value = preVal * nextVal
                else:
                    value *= nextVal

        return value
