import pandas as pd
from typing import Union, Tuple
from adlinear import nmfmodel as nmf
from adlinear import ntfmodel as ntf


class NMFClient:

    def __init__(self):
        self._data = pd.DataFrame
        self._model = nmf.NmfModel(self._data, ncomp=2)
        self._latest_h = pd.DataFrame
        self._latest_w = pd.DataFrame
        self._latest_error = pd.DataFrame
        pass

    def set_data(self, data: pd.DataFrame):
        self._data = data

    def set_ncomp(self, ncomp: int):
        self._model.set_ncomp(ncomp)

    def update_h(self, h_estd: pd.DataFrame):
        pass

    def update_w(self):
        pass


class NMFCentralizer:

    def __init__(self, nfeat: int):
        self._current_H = pd.DataFrame(columns=range(nfeat))
        self._nmfcomp = 1
        self._nfeat = nfeat
        pass

    def set_ncomp(self, ncomp: int):
        self._nmfcomp = ncomp
        self._current_H = pd.DataFrame(columns=range(self._nfeat),
                                       index=range(self._nmfcomp),
                                       data=1)

    def set_nfeat(self, nfeat: int):
        self._nfeat = nfeat
        self._current_H = pd.DataFrame(columns=range(self._nfeat),
                                       index=range(self._nmfcomp),
                                       data=1)

    def request_for_update(self, client: NMFClient):
        pass


class FederatedNMFConfig:

    def __init__(self,
                 nmfcentral: NMFCentralizer,
                 clients: Tuple[NMFClient]):

        self._nmfcentral = nmfcentral
        self._clients = clients
        pass

    def get_central(self) -> NMFCentralizer:
        return self._nmfcentral

    def set_central(self, central: NMFCentralizer):
        self._nmfcentral = central

    def get_clients(self):
        return self._clients

    def set_ncomp(self, ncomp: int):
        for clt in self._clients:
            clt.set_ncomp(ncomp)

    def set_nfeat(self, nfeat: int):
        self._nmfcentral.set_nfeat(nfeat)



