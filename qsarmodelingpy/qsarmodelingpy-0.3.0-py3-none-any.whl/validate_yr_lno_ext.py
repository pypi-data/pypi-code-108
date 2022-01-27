import sys
import numpy as np
import pandas as pd
import json
import logging
from qsarmodelingpy import Utils
from qsarmodelingpy.cross_validation_class import CrossValidation
from qsarmodelingpy.yrandomization import YRandomization
from qsarmodelingpy.lno import LNO
import qsarmodelingpy.lj_cut as lj
from qsarmodelingpy.filter import variance_cut, correlation_cut
from qsarmodelingpy.external_validation import ExternalValidation
import os


def validate(X, y, pop, Q2, Q2_cut=0.5, yr_cut=0.3, lno_cut=0.1):
    # y-randomization
    lpass = []
    intercepts = []
    for i, var_sel in enumerate(pop):
        if Q2[i] > Q2_cut:
            XSel = X[:, var_sel]
            cv = CrossValidation(XSel, y)
            nLV = np.argmax(cv.Q2()) + 1
            yr = YRandomization(XSel, y, nLV, 50)
            intercepts.append(yr.returnIntercept())
            if yr.returnIntercept() < yr_cut:
                lpass.append(i)
    # leave-N-out
    lpass2 = []
    if lpass != []:
        for i in lpass:
            if Q2[i] > Q2_cut:
                XSel = X[:, pop[i]]
                m, _ = np.shape(X)
                cv = CrossValidation(XSel, y)
                nLV = np.argmax(cv.Q2()) + 1
                lno = LNO(XSel, y, nLV, int(m / 4), 5)
                m = np.mean(lno.Q2, 1)
                std = max([abs(m[j] - m[0]) for j in range(len(m))])
                if std < lno_cut:
                    lpass2.append(i)
        if lpass2 != []:
            return lpass2
        else:
            return []
    else:
        return []


def validate_ext(X, y, test, pop, Q2):
    train = [j for j in range(len(y)) if j not in test]
    passed = validate(X, y, pop, Q2)
    lpass = []
    pop_pass = []
    for i in passed:
        var_sel = pop[i]
        XSel = X[:, var_sel]
        cv = CrossValidation(XSel, y)
        nLV = np.argmax(cv.Q2()) + 1
        ext = ExternalValidation(XSel, y, nLV)
        if ext.validateExtVal(train, test, nLV):
            lpass.append(i)
            pop_pass.append(var_sel)
    return pop_pass


if __name__ == '__main__':
    directory = sys.argv[1]
    df = Utils.load_matrix(os.path.join(directory, sys.argv[2]))
    dfX = lj.transform(df)
    y = pd.read_csv(os.path.join(
        directory, sys.argv[3]), header=None).values
    indVar = variance_cut(dfX.values, 0.1)
    dfVar = dfX.loc[:, dfX.columns[indVar]]
    print(dfVar.shape)
    indCorr = correlation_cut(dfVar.values, y, 0.3)
    dfCorr = dfVar.loc[:, dfVar.columns[indCorr]]
    print(dfCorr.shape)
    out_directory = sys.argv[4]
    X = dfCorr.values
    with open(directory + "/Popout.json") as pop_file:
        pop = json.load(pop_file)
    with open(directory + "/Q2out.json") as Q2_file:
        Q2 = json.load(Q2_file)
    var_sel = validate(X, y, pop, Q2, yr_cut=0.25, lno_cut=0.1)
    if var_sel != []:
        dfSel = dfCorr.loc[:, dfCorr.columns[var_sel]]
        dfSel.to_csv(out_directory + "/XSel.csv", sep=';')
        cv = CrossValidation(dfSel.values, y)
        cv.saveParameters(out_directory + "/parameters_cv.csv")
    else:
        logging.warn("y-randomization or LNO failed!")
