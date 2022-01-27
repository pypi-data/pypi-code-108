from typing import Optional
from qsarmodelingpy.plsbdg import *
import numpy as np
from math import sqrt


class Outliers(object):
    def __init__(self, X, y, n_components=1, scale=True):
        self.X = X
        self.y = y
        self.nLV = n_components
        self.scale = scale
        self.__leverage: Optional[np.ndarray] = None

    def leverage(self) -> np.ndarray:
        pls = PLSBidiag(self.nLV, self.scale)
        pls.fit(self.X, self.y)
        U, S = pls.U, pls.S
        m, n = np.shape(U)
        sinal = 1
        T = np.zeros((m, n))
        for i in range(m):
            for j in range(n):
                T[i, j] = U[i, j] * S[j, j] * sinal
                sinal = -sinal

        Aux = np.linalg.inv((T.T).dot(T))
        self.__leverage = np.zeros(m)
        for i in range(m):
            self.__leverage[i] = T[i, :].dot(Aux).dot(T[i, :].T)

        return self.__leverage

    def rstd(self) -> np.ndarray:
        pls = PLSBidiag(self.nLV, self.scale)
        pls.fit(self.X, self.y)
        ycal = pls.predict(self.X)[:, self.nLV - 1]
        m, _ = self.X.shape
        lev = self.__leverage or self.leverage()
        one_minus_lev = np.ones(m) - lev
        residuals = np.reshape(self.y, m) - ycal
        lresc = 1 / (m - 1) * (residuals / one_minus_lev * 1 / one_minus_lev)
        lresc = lresc.dot(residuals)
        rstd = 1 / sqrt(lresc) * residuals / np.sqrt(one_minus_lev)
        return rstd
