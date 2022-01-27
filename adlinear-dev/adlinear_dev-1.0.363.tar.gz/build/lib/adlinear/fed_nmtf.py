import pandas as pd
import numpy as np
from typing import Union, Tuple
from adlinear import nmfmodel as nmf
from adlinear import ntfmodel as ntf
import math


class NMFClient:

    def __init__(self, name: str):
        self._name = name
        self._data = pd.DataFrame()
        self._model: nmf.NmfModel = nmf.NmfModel(self._data, ncomp=2)
        self._latest_h = pd.DataFrame
        self._latest_w = pd.DataFrame
        self._latest_error: float = 1.0
        self._latest_error_delta: float = 0.0
        self._niter = 0
        pass

    def reset(self):
        self._latest_error = 1.0
        self._latest_error_delta = 0.0
        self._niter = 0

    def get_ncomp(self) -> int:
        return self._model.ncomp

    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str):
        self._name = name

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
        self._niter += 1
        pass

    def get_latest_h(self) -> pd.DataFrame:
        return self._latest_h

    def get_latest_error(self) -> float:
        return self._latest_error

    def get_latest_error_delta(self) -> float:
        return self._latest_error_delta

    def get_count(self) -> int:
        return self._niter


class NMFCentralizer:

    def __init__(self, nfeat: int, ):
        self._current_h = pd.DataFrame(index=range(nfeat))
        self._nmfcomp = 1
        self._nfeat = nfeat
        self._learning_rate = 0.1
        self._err = 1
        self._niter = 0
        return

    def reset(self):
        self._current_h = pd.DataFrame(index=range(self._nfeat),
                                       columns=range(self._nmfcomp),
                                       data=np.ones((self._nfeat, self._nmfcomp)))
        self._err = 1
        self._niter = 0
        return

    def set_ncomp(self, ncomp: int):
        self._nmfcomp = ncomp
        self._current_h = pd.DataFrame(index=range(self._nfeat),
                                       columns=range(self._nmfcomp),
                                       data=np.ones((self._nfeat, self._nmfcomp)))
        return

    def set_features(self, features: Tuple[str]):
        self._nfeat = len(features)
        self._current_h = pd.DataFrame(index=features,
                                       columns=range(self._nmfcomp),
                                       data=np.ones((self._nfeat, self._nmfcomp)))
        return

    def err(self):
        return self._err

    def set_h_guess(self, h: pd.DataFrame):
        self._current_h = h.copy()

    def request_for_update(self, client: NMFClient):
        client.update_h(self._current_h)
        h = client.get_latest_h()
        err_clt = client.get_latest_error()
        w_clt = math.exp(- self._learning_rate * err_clt)
        w_self = math.exp(- self._learning_rate * self._err) if self._niter > 0 else 0
        assert len(self._current_h.columns) == len(h.columns)
        self._current_h.columns = h.columns
        self._current_h = w_clt * h + w_self * self._current_h
        self._current_h = self._current_h / (w_clt + w_self)
        self._err = (w_clt * err_clt + w_self * self._err) / (w_clt + w_self)
        self._niter += 1
        pass


class FederatedNMFConfig:

    def __init__(self,
                 nmfcentral: NMFCentralizer,
                 clients: Tuple[NMFClient]):

        self._nmfcentral: NMFCentralizer = nmfcentral
        self._clients: Tuple[NMFClient] = []
        self.set_clients(clients, [])
        pass

    def set_clients(self, clients: Tuple[NMFClient], names: Tuple[str] = []):
        nclients = len(clients)
        if len(names) == 0:
            names = [f"Client {i+1}" for i in range(nclients)]
        else:
            pass
        assert len(names) == nclients
        self._clients = clients
        for iclt, clt in enumerate(self._clients):
            clt.set_name(names[iclt])

    def set_client_names(self, names: Tuple[str] = []):
        nclients = len(self._clients)
        if len(names) == 0:
            names = [f"Client {i+1}" for i in range(nclients)]
        else:
            pass
        assert len(names) == nclients
        for iclt, clt in enumerate(self._clients):
            clt.set_name(names[iclt])

    def get_central(self) -> NMFCentralizer:
        return self._nmfcentral

    def set_central(self, central: NMFCentralizer):
        self._nmfcentral = central

    def get_clients(self):
        return self._clients

    def set_ncomp(self, ncomp: int):
        self._nmfcentral.set_ncomp(ncomp)
        for clt in self._clients:
            clt.set_ncomp(ncomp)

    def set_features(self, features: Tuple[str]):
        self._nmfcentral.set_features(features)

    def request_update_step(self, client_idx: int):
        if 0 <= client_idx <= len(self._clients):
            clt = self._clients[client_idx]
            self._nmfcentral.request_for_update(clt)

    def request_full_round(self):
        for iclt, clt in enumerate(self._clients):
            self._nmfcentral.request_for_update(clt)
            clt_count = clt.get_count()
            print(f"After checking {clt.get_name()}, trial {clt_count}: erreur: {self._nmfcentral.err()}")

    def reset_counters(self):
        self._nmfcentral.reset()
        for clt in self._clients:
            clt.reset()



