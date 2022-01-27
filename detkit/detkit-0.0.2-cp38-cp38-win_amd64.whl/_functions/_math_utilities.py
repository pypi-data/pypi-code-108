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
import scipy
import scipy.linalg

__all__ = ['logdet', 'triang_logdet']


# ======
# logdet
# ======

def logdet(A, sym_pos=False):
    """
    Finds logdet of a matrix.
    """

    if sym_pos:
        L = scipy.linalg.cholesky(A, lower=True)
        logdet_, sign = triang_logdet(L)
        logdet_ = 2.0 * logdet_

    else:
        lu, p = scipy.linalg.lu_factor(A)
        logdet_, sign = triang_logdet(lu, p)

    return logdet_, sign


# =============
# triang logdet
# =============

def triang_logdet(lu, p=None):
    """
    Computes the logdet of a triangular matrix. The input matrix lu is an
    lu_factor, meaning that it contains L on its lower diagonals and U on its
    upper diagonals. L has diagonals 1 and is not stored in lu. The diagonals
    of lu are the diagonals of U.
    """

    diag = numpy.diag(lu)

    if numpy.any(diag == 0):
        logdet_ = -numpy.inf
        sign = 0
    else:
        logdet_ = numpy.sum(numpy.log(numpy.abs(diag)))
        sign = numpy.sign(0.5 - (numpy.sum((diag < 0)) % 2))

        # Permutation matrix
        if p is not None:
            # Find the number of permutations
            no_perm = numpy.arange(p.size)
            diff = p - no_perm

            # Find which of the elements of diff are non-zero
            num_perm = numpy.sum(diff != 0)

            # If there are odd number of permutations, flip sign
            if num_perm % 2 == 1:
                sign = -sign

    return logdet_, sign
