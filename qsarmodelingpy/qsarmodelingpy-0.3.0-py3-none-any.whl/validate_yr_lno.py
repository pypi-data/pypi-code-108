import sys
from typing import TypedDict, Union, Tuple
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


class YRResult(TypedDict):
    passed: bool
    score: float
    yr: YRandomization


class LNOResult(TypedDict):
    passed: bool
    score: float
    lno: LNO


class ValidateYRLNOResult(TypedDict):
    passed: bool
    yr_result: YRResult
    lno_result: LNOResult


def run_yrandomization(X: pd.DataFrame, y: np.ndarray, yr_cut: float = 0.3) -> YRResult:
    """Run y-randomization on the data.

    Args:
        X (pd.DataFrame): The matrix with desired features.
        y (np.ndarray): The vector with the response.
        yr_cut (float, optional): The maximum score to pass in yrandomization. Defaults to 0.3.

    Returns:
        Tuple[bool, float]: A tuple containing the status of the y-randomization (true if passed, false otherwise) and the score.
    """
    cv = CrossValidation(X, y)
    nLV = np.argmax(cv.Q2()) + 1
    yr = YRandomization(X, y, nLV, 50)
    intercept = yr.returnIntercept()

    passed = intercept < yr_cut
    return YRResult({"passed": passed, "score": intercept, "yr": yr})


def run_leavenout(X: pd.DataFrame, y: np.ndarray, lno_cut: float = 0.1) -> LNOResult:
    """Run Leave-N-Out on the data.

    Args:
        X (pd.DataFrame): The matrix with desired features.
        y (np.ndarray): The vector with the response.
        yr_cut (float, optional): The maximum score to pass in Leave-N-Out. Defaults to 0.1.

    Returns:
        Tuple[bool, float]: A tuple containing the status of the Leave-N-Out (true if passed, false otherwise) and the score.
    """
    m, _ = np.shape(X)
    cv = CrossValidation(X, y)
    nLV = np.argmax(cv.Q2()) + 1
    lno = LNO(X, y, nLV, int(m / 4), 5)
    m = np.mean(lno.Q2, 1)
    std = max([abs(m[j] - m[0]) for j in range(len(m))])

    passed = std < lno_cut
    return LNOResult({"passed": passed, "score": std, "lno": lno})


def validate(X: np.ndarray, y: np.ndarray, pop: Union[np.ndarray, list], Q2: Union[np.ndarray, list], Q2_cut=0.5, yr_cut=0.3, lno_cut=0.1) -> list:
    # y-randomization
    lpass = []
    intercepts = []
    for i, var_sel in enumerate(pop):
        if Q2[i] > Q2_cut:
            # TODO: use run_yrandomization()
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
                # TODO: use run_leavenout()
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
            i = np.argmax([Q2[i] for i in lpass2])
            var_sel = pop[lpass2[i]]
            return var_sel
        else:
            return []
    else:
        return []


if __name__ == '__main__':
    directory = sys.argv[1]
    df = Utils.load_matrix(sys.argv[2])
    dfX = lj.transform(df)
    y = pd.read_csv(sys.argv[3], sep=';', header=None).values
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
