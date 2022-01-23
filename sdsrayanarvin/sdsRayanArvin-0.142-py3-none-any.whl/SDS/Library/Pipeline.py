from sdsRayanArvin.Dataset.AuxStationData import Aux
from sdsRayanArvin.RepositoryApi.DataApi import Data


class Pipeline:
    def GetLastData(self, Aux_data: Aux, deviceData: Data):
        if Aux_data is None:
            return 0

        type_aux = None

        if Aux_data.type == 1:
            type_aux = 'DO'
        if Aux_data.type == 2:
            type_aux = 'DI'
        if Aux_data.type == 3:
            type_aux = 'AI'
        if Aux_data.type == 5:
            type_aux = 'VDO'
        if Aux_data.type == 6:
            type_aux = 'AII'
        if Aux_data.type == 8:
            return self.ReplaceTagWithValue(Aux_data, deviceData)

        if type_aux is None:
            return

        Last_data = deviceData.LastDataOnTopic(str(Aux_data.code),
                                               str(type_aux),
                                               str(Aux_data.pan),
                                               str(Aux_data.address))

        if Last_data is not None:
            if Aux_data.type == 1 or Aux_data.type == 2 or Aux_data.type == 5:
                binOutput = "{0:b}".format(int(Last_data.getData()))
                binOutputArray = list(binOutput)
                binOutputArray.reverse()
                idxOutput = Aux_data.output - 1
                if len(binOutputArray) > idxOutput:
                    return binOutputArray[idxOutput]
                else:
                    return 0

            return Last_data.getData()
        else:
            return 0

    def ReplaceTagWithValue(self, Aux_data: Aux, deviceData: Data):
        arrayMath = Aux_data.Analog.math.split(' ')
        tag = arrayMath[0]
        Last_data = deviceData.LastDataOnTopic(str(Aux_data.code),
                                               str(tag),
                                               str(Aux_data.pan),
                                               str(Aux_data.address))
        data = Last_data.getData()

        data = 0 if data is None else data

        finalData = Aux_data.Analog.math.replace(tag, data)

        return self.ReplaceMathWithValue(finalData)

    def ReplaceMathWithValue(self, value):
        arrayMath = value.split(' ')
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
