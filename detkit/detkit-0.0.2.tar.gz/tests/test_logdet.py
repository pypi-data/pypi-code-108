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
from detkit import logdet


# ===========
# test logdet
# ===========

def test_logdet():
    """
    """

    n = 500
    A = numpy.random.rand(n, n)

    sym_pos = True

    if sym_pos:
        A = A.T @ A

    print(numpy.linalg.slogdet(A))
    logdet_, sign = logdet(A, sym_pos=sym_pos)
    print(logdet_)
    print(sign)


# ===========
# Script main
# ===========

if __name__ == "__main__":
    test_logdet()
