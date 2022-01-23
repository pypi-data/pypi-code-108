from sdsRayanArvin.Dataset.AuxStationData import AuxStationData
from sdsRayanArvin.Repository import Repository


class AuxStation(Repository):
    def AuxAll(self):
        res = self.Request.sendWithToken('GET', 'aux_all')
        auxs = []
        for aux in res['Aux']:
            auxs.append(AuxStationData(aux).aux)
        return auxs

    def AuxOnID(self, ID_AUX_station):
        # if self.Request.getCache('aux/' + ID_AUX_station) is not None:
        #     return self.Request.getCache('aux/' + ID_AUX_station)
        # else:
        #     res = self.Request.sendWithToken('GET', 'aux/' + ID_AUX_station)
        #     data = AuxStationData(res['Aux']).aux
        #     self.Request.setCache('aux/' + ID_AUX_station, data)
        #     return data
        res = self.Request.sendWithToken('GET', 'aux/' + ID_AUX_station)
        return AuxStationData(res['Aux']).aux