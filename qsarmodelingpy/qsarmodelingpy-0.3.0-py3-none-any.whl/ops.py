import numpy as np
from qsarmodelingpy.cross_validation_class import CrossValidation
from qsarmodelingpy.plsbdg import PLSBidiag
from sklearn.preprocessing import scale as autoscale
import operator
import json
import logging
import pandas as pd


class OPS(object):
    def __init__(self, X: pd.DataFrame, y: pd.DataFrame, nLV: int = None, nLVModel: int = None, window: int = 2, increment: int = 1, percentage=100,
                 nModels=100, scale=True):
        super(OPS, self).__init__()
        self.X = autoscale(X) if scale else X
        self.y = autoscale(y) if scale else y
        self.nLV = min(np.shape(X)) if nLV is None else nLV
        self.nLVModel = int(np.shape(X)[0]/5) if nLVModel is None else nLVModel
        if window >= 2:
            self.window = window
        else:
            self.window = 2
            logging.warning(
                "For OPS, window parameter must be at least 2. Continuing with this value.")
        self.increment = increment
        self.percentage = percentage
        self.nModels = nModels
        self.vars = np.array(range(np.shape(X)[1]))

    def vectors(self, X, y, nLV):
        correlogram = abs(
            np.dot(np.transpose(autoscale(X)), autoscale(y))/(len(y)-1))
        pls = PLSBidiag(nLV)
        pls.fit(X, y)
        reg = abs(pls.B)
        vec = abs(np.append(correlogram, reg, axis=1))
        norms = np.linalg.norm(vec, ord=np.inf, axis=0)
        for i in range(len(norms)):
            vec[:, i] = vec[:, i]/norms[i]
        for i in range(1, len(norms)):
            vec = np.c_[vec, np.multiply(vec[:, 0], vec[:, i])]
        return vec

    def runOPS(self, X=None, y=None):
        if X is None:
            X = self.X
        if y is None:
            y = self.y
        nLVModel = self.nLVModel
        m, n = np.shape(X)
        vec = self.vectors(X, y, self.nLV)
        nVec = 2*self.nLV+1
        maxVar = self.percentage*n/100
        models = {}
        models["Q2"] = []
        models["var_sel"] = []
        Q2 = np.zeros(0)
        var_sel = []
        for i in range(nVec):
            logging.info("Running vector {} of {}".format(i+1, nVec))
            # ordenar em ordem decrescente, por isso o -vec
            ind = np.argsort(-vec[:, i])
            Xor = X[:, ind]
            nVar = self.window
            while nVar <= maxVar:
                Xev = Xor[:, 0:nVar]
                cv = CrossValidation(Xev, y, nLVModel)
                # models["Q2"].append(max(cv.Q2()))
                # models["var_sel"].append(ind[0:nVar])
                Q2 = np.append(Q2, max(cv.Q2()))
                # var_sel.append(self.vars[ind[0:nVar]].tolist())
                var_sel.append([int(self.vars[ind[i]]) for i in range(nVar)])
                nVar += self.increment
            indSort = np.argsort(-Q2).tolist()
            Q2 = Q2[indSort]
            var_sel = [var_sel[k] for k in indSort]
            Q2 = Q2[0:min(self.nModels, len(Q2))]
            var_sel = var_sel[0:min(self.nModels, len(var_sel))]
        models["Q2"] = Q2.tolist()
        models["var_sel"] = var_sel
        self.models = models

    def feedOPS(self):
        print("First run of OPS")
        self.runOPS()
        var_sel1 = []
        X = self.X
        y = self.y
        Q2 = 0
        # and np.sort(var_sel1) != np.sort(self.models["var_sel"][0]):
        while Q2 < self.models["Q2"][0]:
            var_sel1 = self.models["var_sel"][0]
            Q2 = self.models["Q2"][0]
            print("{} variables were selected in the previous step of OPS run".format(
                len(var_sel1)))
            X = self.X[:, var_sel1]
            self.vars = var_sel1
            # with less than 100 variables we could run OPS with 100 % of variables
            if np.shape(X)[1] < 100:
                self.percentage = 100
            self.nLV = min(np.shape(X))
            self.runOPS(X, y)

    def saveModels(self, file):
        with open(file, "w") as models_file:
            models_file.write(json.dumps(self.models))
