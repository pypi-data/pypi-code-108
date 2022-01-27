import pandas as pd
from qsarmodelingpy.leaveNout import LeaveNout
import numpy as np
from sklearn.cross_decomposition import PLSRegression
import qsarmodelingpy.calculate_parameters as cp


class LNO(object):

    def __init__(self, X, y, nLV, n=None, nrepeat=5):
        self.X = X if isinstance(X, pd.DataFrame) else pd.DataFrame(X)
        self.y = y
        self.nLV = nLV if nLV is not None else len(y)/5
        self.n = n if n is not None else int(len(y)/4)
        self.nrepeat = nrepeat
        ycv = np.zeros((len(y), 1))
        self.Q2 = np.zeros((self.n, nrepeat))
        i = 0
        pls = PLSRegression(n_components=nLV)
        n_samples = np.shape(X)[0]
        for i in range(self.n):
            lno = LeaveNout(i+1, n_repeats=self.nrepeat)
            nsplits = int(n_samples/(i+1))
            if n_samples % (i+1) != 0:
                nsplits += 1
            j = 0
            k = 0
            for train, test in lno.split(X):
                pls.fit(self.X.iloc[train, :], y[train])
                ycv[test, :] = pls.predict(self.X.iloc[test, :])
                j = (j+1) % nsplits
                if j == 0:
                    self.Q2[i, k] = cp.calcR2(self.y, ycv)
                    k = k + 1
