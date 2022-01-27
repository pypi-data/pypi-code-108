import numpy as np

from biofilm import util
import structout as so
from ubergauss import tools

from biofilm.algo import feature_selection as fs

"""
- get 2 test datasets, csr and a normal one...
"""


def main():
    XYxy, feat, inst  = util.getfold()
    X,Y,x,y = XYxy
    X = tools.zehidense(X)

    # labels:
    print(f"labels {np.unique(Y)=}")


    print("CORRELATION TO TARGET")
    so.lprint( tools.spearman(X,Y) )


    print("Performance Forest")
    print(fs.f1_score(y,fs._forest(X,Y)[1].predict(x)))

    print("CORRELATION, Closest feature")
    so.lprint([max(tools.spearman(X,X[:,i])) for i in range(X.shape[1]) ])

    # imbalance
    print("DATASET IMBALANCE")
    print(sum(Y==1)/X.shape[0])

    # Shape
    print("{X.shape=}")

    # inf/nan in file?
    print("{np.isfinite(X).all()=}")



if __name__ == "__main__":
    main()
