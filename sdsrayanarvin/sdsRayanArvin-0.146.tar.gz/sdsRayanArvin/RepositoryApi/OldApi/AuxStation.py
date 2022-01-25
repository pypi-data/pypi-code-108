from sdsRayanArvin.Dataset.AuxStationData import AuxStationData
from sdsRayanArvin.Repository import Repository


class AuxStation(Repository):
    def AuxAll(self):
        res = self.Request.sendWithToken('GET', 'aux_all')
        auxs = []
        try:
            for aux in res['Aux']:
                auxs.append(AuxStationData(aux).aux)
            return auxs
        except:
            return auxs

    def AuxOnID(self, ID_AUX_station):
        res = self.Request.sendWithToken('GET', 'aux/' + ID_AUX_station)
        try:
            return AuxStationData(res['Aux']).aux
        except:
            return []
