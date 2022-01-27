#! /usr/bin/env python

# SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the license found in the LICENSE.txt file in the root directory
# of this source tree.


# =======
# Imports
# =======

import numpy
import numpy.linalg
from detkit import plogdet, py_plogdet, orthogonalize


# ===========
# test logdet
# ===========

def test_logdet():
    """
    """

    n = 100
    m = 5
    A = numpy.random.rand(n, n)
    X = numpy.random.rand(n, m)

    # Make A a PSD matrix, and make X orthogonal
    A = A.T @ A

    sym_pos = True
    X_orth = False

    if X_orth:
        orthogonalize(X)

    XtX = X.T @ X
    C = X.T @ numpy.linalg.inv(A) @ X
    sign_00, logdet_00 = numpy.linalg.slogdet(A)
    sign_01, logdet_01 = numpy.linalg.slogdet(C)
    sign_02, logdet_02 = numpy.linalg.slogdet(XtX)
    sign_0 = sign_00
    logdet_0 = logdet_02 - logdet_00 - logdet_01

    XtXinv = numpy.linalg.inv(XtX)
    P = X @ XtXinv @ X.T
    N = A + P - A @ P
    logdet_3 = -numpy.linalg.slogdet(N)[1]
    print('%16.8f' % logdet_3)

    logdet_1, sign_1, flops_1 = plogdet(A, X, method='legacy', sym_pos=sym_pos,
                                        X_orth=X_orth, flops=True)
    logdet_2, sign_2, flops_2 = plogdet(A, X, method='proj', sym_pos=False,
                                        X_orth=X_orth, flops=True)
    logdet_3, sign_3 = py_plogdet(A, X, method='legacy', sym_pos=sym_pos,
                                  X_orth=X_orth)
    logdet_4, sign_4 = py_plogdet(A, X, method='proj', sym_pos=False,
                                  X_orth=X_orth)
    print('%16.8f, %+d' % (logdet_0, sign_0))
    print('%16.8f, %+d, %ld' % (logdet_1, sign_1, flops_1))
    print('%16.8f, %+d, %ld' % (logdet_2, sign_2, flops_2))
    print('%16.8f, %+d' % (logdet_3, sign_3))
    print('%16.8f, %+d' % (logdet_4, sign_4))


# ===========
# Script main
# ===========

if __name__ == "__main__":
    test_logdet()
