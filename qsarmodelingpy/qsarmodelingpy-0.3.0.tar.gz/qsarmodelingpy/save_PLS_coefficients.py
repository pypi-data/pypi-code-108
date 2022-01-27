import numpy as np
import pandas as pd
from qsarmodelingpy.cross_validation_class import CrossValidation
from qsarmodelingpy.plsbdg import PLSBidiag


def save_coefficients(dfX: pd.DataFrame, dfy: pd.DataFrame, out_file: str = "B", nLV=None):
    X = dfX.values if type(dfX) == pd.DataFrame else dfX
    y = dfy.values if type(dfy) == pd.DataFrame else dfy
    if nLV == None:
        cv = CrossValidation(X, y)
        nLV = np.argmax(cv.Q2()) + 1
    pls = PLSBidiag(nLV)
    pls.fit(X, y)
    dfB = pd.DataFrame(np.vstack((pls.B, pls.indT)))
    ind = list(dfX.columns)
    ind.append("indT")
    dfB.index = ind
    dfB.columns = ["LV" + str(i + 1) for i in range(nLV)]
    # Normalizes the filename removing the extension, if any
    if out_file.endswith(".csv"):
        out_file = out_file[:-4]
    dfB.to_csv(out_file + ".csv")
    dfBproc = pd.DataFrame(pls.Bproc)
    dfBproc.columns = dfB.columns
    dfBproc.index = dfX.columns
    dfB.to_csv(out_file + "_proc.csv")
