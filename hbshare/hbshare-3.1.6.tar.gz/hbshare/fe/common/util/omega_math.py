# -*- coding: utf-8 -*-

import numpy as np


def calc_volatility(X, F, var, h, is_aligned=False):
    if is_aligned:
        idx = X.index.intersection(h.index).intersection(var.index)
        X_cp = np.mat(X.reindex(idx).values)
        h_cp = np.mat(h.reindex(idx)).T
        D = np.mat(np.diag(var.reindex(idx)))
    else:
        X_cp = np.mat(X.values)
        h_cp = np.mat(h).T
        D = np.mat(np.diag(var))
    F_cp = np.mat(F.values)
    b = X_cp.T * h_cp
    common = b.T * F_cp * b
    specific = h_cp.T * D * h_cp

    return common[0, 0] + specific[0, 0]


def calc_covariance(X, F, var, h1, h2):
    X = np.mat(X.values)
    F = np.mat(F.values)
    D = np.mat(np.diag(var))
    h1 = np.mat(h1)
    h2 = np.mat(h2).T

    a = h1 * X
    b = X.T * h2
    common = a * F * b
    specific = h1 * D * h2

    return common[0, 0] + specific[0, 0]
