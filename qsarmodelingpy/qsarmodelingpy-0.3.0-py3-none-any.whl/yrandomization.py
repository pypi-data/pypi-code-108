import random
from qsarmodelingpy.cross_validation_class import CrossValidation
import numpy as np
from sklearn.preprocessing import scale
from sklearn import linear_model


class YRandomization(object):
    def __init__(self, X, y, nLV, nrd=50):
        self.X = X
        self.y = y
        self.nLV = nLV
        self.nrd = nrd
        self.Q2 = []
        self.R2 = []
        self.R = []
        self.RMSECV = []
        for _ in range(nrd):
            yrd = y[random.sample(range(len(y)), len(y))]
            cv = CrossValidation(X, yrd, nLV)
            self.Q2.append(cv.Q2()[nLV-1])
            self.R2.append(cv.R2()[nLV-1])
            self.RMSECV.append(cv.RMSECV()[nLV-1])
            r = np.dot(np.transpose(scale(y)), scale(yrd))/(len(y))
            self.R.append(r[0][0])
        cv = CrossValidation(X, y, nLV)
        self.Q2.append(cv.Q2()[nLV-1])
        self.R2.append(cv.R2()[nLV-1])
        self.RMSECV.append(cv.RMSECV()[nLV-1])
        r = np.dot(np.transpose(scale(y)), scale(y))/(len(y))
        self.R.append(r[0][0])

    def returnIntercept(self):
        reg = linear_model.LinearRegression()
        reg.fit(np.array(self.R).reshape(-1, 1),
                np.array(self.R2).reshape(-1, 1))
        return reg.intercept_

    def returnRegResultsR2(self):
        reg = linear_model.LinearRegression()
        reg.fit(np.array(self.R).reshape(-1, 1),
                np.array(self.R2).reshape(-1, 1))
        return reg.coef_, reg.intercept_

    def returnRegResultsQ2(self):
        reg = linear_model.LinearRegression()
        reg.fit(np.array(self.R).reshape(-1, 1),
                np.array(self.Q2).reshape(-1, 1))
        return reg.coef_, reg.intercept_
