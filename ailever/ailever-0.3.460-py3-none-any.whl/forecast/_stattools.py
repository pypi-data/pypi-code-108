import numpy as np
from numpy import linalg

def regressor(norm):
    r"""
    Args:
        norm:
    Examples:
        >>> from ailever.forecast.STOCK import krx
        >>> from ailever.forecast.STOCK import regressor
        >>> from ailever.machine.NM import scaler
        >>> import numpy as np
        >>> import FinanceDataReader as fdr
        >>> import matplotlib.pyplot as plt
        >>> ...
        >>> plt.rcParams["font.family"] = 'NanumBarunGothic'
        >>> ...
        >>> df = krx.kospi('2018-01-01')
        >>> norm = scaler.standard(df[0][-300:])
        >>> yhat = regressor(norm)
        >>> ...
        >>> container = yhat[-1,:] - yhat[0,:]
        >>> index = np.where(container>=2)[0]
        >>> ...
        >>> plt.figure(figsize=(12,15))
        >>> for symbol, name in zip(df[1].iloc[index].Symbol, df[1].iloc[index].Name):
        >>>     x = fdr.DataReader(f'{symbol}').Close.values[-300:]
        >>>     plt.plot(x, label=name)
        >>>     plt.text(len(x), x[-1], name)
        >>> plt.legend()
        >>> plt.show()
        >>> ...
        >>> df[1].iloc[index] 
    """
    x, y = list(range(len(norm))), norm
    bias = np.ones_like(x)
    X = np.c_[bias, x]

    b = linalg.inv(X.T@X) @ X.T @ y
    yhat = X@b
    return yhat


class scaler:
    @staticmethod
    def standard(X):
        X = (X - X.mean(axis=0))/X.std(ddof=1)
        return X

    @staticmethod
    def minmax(X):
        X = (X - X.min(axis=0))/(X.max(axis=0)-X.min(axis=0))
        return X
