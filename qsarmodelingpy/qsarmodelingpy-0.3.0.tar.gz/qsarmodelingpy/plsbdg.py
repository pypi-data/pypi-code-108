import numpy as np
from sklearn.preprocessing import scale


def normalize(v):
    (m, n) = np.shape(v)
    fn = np.zeros(n)
    vn = np.zeros((m, n))
    for i in range(n):
        fn[i] = np.linalg.norm(v[:, i])
        vn[:, i] = v[:, i]/fn[i]
    return vn, fn


class PLSBidiag(object):
    """[PLS Bidiagonal](https://onlinelibrary.wiley.com/doi/abs/10.1002/cem.1309) method.
    """

    def __init__(self, n_components=1, scale=True):
        self.nLV = n_components
        self.scale = scale

    def bdiag(self, a, y):
        nLV = self.nLV
        (nrow, ncol) = np.shape(a)
        v = np.zeros((ncol, nLV))
        w = np.zeros(nLV)
        u = np.zeros((nrow, nLV))
        rv1 = np.zeros(nLV)
        for i in range(nLV):
            vi = normalize(np.dot(np.transpose(a), y))[0]
            ui = np.dot(a, vi)
            if i == 0:
                ui, nor = normalize(ui)
            else:
                temp = np.dot(np.transpose(u), ui)
                rv1[i-1] = temp[i-1]
                ui, nor = normalize(ui - np.dot(u, temp))
            w[i] = nor[0]
            v[:, i] = vi[:, 0]
            u[:, i] = ui[:, 0]
            if i < nLV-1:
                y = y - np.dot(ui, np.dot(np.transpose(ui), y))
        return u, w, rv1, v

    def fit(self, X, y):
        if self.scale:
            a = scale(X)
            yt = scale(y)
        else:
            a = X
            yt = yt
        U, w, rv1, V = self.bdiag(a, yt)
        S = np.diag(w) + np.diag(rv1[:-1], 1)
        m, n = np.shape(X)
        nLV = self.nLV
        B = np.zeros((n, nLV))
        for i in range(nLV):
            c = np.dot(np.transpose(U[:, 0:(i+1)]), yt)
            q = np.linalg.solve(S[0:i+1, 0:i+1], c)
            B[:, i] = np.dot(V[:, 0:(i+1)], q)[:, 0]
        self.Bproc = B
        self.B, self.indT = self.reprocessB(X, y)
        self.U = U
        self.S = S
        self.V = V

    def reprocessB(self, X, y):
        stdy = np.std(y)
        meany = np.mean(y)
        stdX = np.std(X, 0)
        meanX = np.mean(X, 0)
        m, n = np.shape(X)
        nLV = self.nLV
        B = np.zeros((n, nLV))
        indT = np.zeros(nLV)
        Bproc = self.Bproc
        for i in range(nLV):
            B[:, i] = Bproc[:, i]*stdy
            B[:, i] = np.divide(B[:, i], np.transpose(stdX))
            t = np.divide(Bproc[:, i], np.transpose(stdX))
            t = t*stdy
            t = np.dot(meanX, t)
            t = -t + meany
            indT[i] = t
        return B, indT

    def predict(self, X):
        B = self.B
        indT = self.indT
        yp = np.dot(X, B)
        for i in range(len(indT)):
            yp[:, i] = yp[:, i] + indT[i]
        return yp
