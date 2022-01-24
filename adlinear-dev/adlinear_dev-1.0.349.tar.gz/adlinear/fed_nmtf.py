import pandas as pd
from typing import Union, Tuple
from adlinear import nmfmodel as nmf
from adlinear import ntfmodel as ntf
import math


class NMFClient:

    def __init__(self):
        self._data = pd.DataFrame()
        self._model: nmf.NmfModel = nmf.NmfModel(self._data, ncomp=2)
        self._latest_h = pd.DataFrame
        self._latest_w = pd.DataFrame
        self._latest_error: float = 0.0
        self._latest_error_delta: float = 0.0
        pass

    def get_ncomp(self) -> int:
        return self._model.ncomp

    def set_data(self, data: pd.DataFrame):
        self._data = data
        ncomp = self._model.ncomp
        self._model = nmf.NmfModel(self._data, ncomp=ncomp)

    def set_ncomp(self, ncomp: int):
        self._model.set_ncomp(ncomp)

    def update_h(self, h_estd: pd.DataFrame):
        self._model.update_h(h_estd)
        self._latest_h = self._model.get_h()
        self._latest_w = self._model.get_w()
        err = self._latest_error
        self._latest_error = self._model.get_precision(relative=True)
        self._latest_error_delta = self._latest_error - err
        pass

    def get_latest_h(self) -> pd.DataFrame:
        return self._latest_h

    def get_latest_error(self) -> float:
        return self._latest_error

    def get_latest_error_delta(self) -> float:
        return self._latest_error_delta


class NMFCentralizer:

    def __init__(self, nfeat: int):
        self._current_h = pd.DataFrame(columns=range(nfeat))
        self._nmfcomp = 1
        self._nfeat = nfeat
        self._learning_rate = 0.1
        self._err = 1
        return

    def set_ncomp(self, ncomp: int):
        self._nmfcomp = ncomp
        self._current_h = pd.DataFrame(columns=range(self._nfeat),
                                       index=range(self._nmfcomp),
                                       data=1)
        return

    def set_nfeat(self, nfeat: int):
        self._nfeat = nfeat
        self._current_h = pd.DataFrame(columns=range(self._nfeat),
                                       index=range(self._nmfcomp),
                                       data=1)
        return

    def request_for_update(self, client: NMFClient):
        client.update_h(self._current_h)
        h = client.get_latest_h()
        err_clt = client.get_latest_error()
        w_clt = math.exp(- self._learning_rate * err_clt)
        w_self = math.exp(- self._learning_rate * self._err)
        self._current_h = w_clt * h + w_self * self._current_h
        self._current_h /= w_clt + w_self
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

    def request_update_step(self, index: int):
        if 0 <= index <= len(self._clients):
            clt = self._clients[index]
            self._nmfcentral.request_for_update(clt)



