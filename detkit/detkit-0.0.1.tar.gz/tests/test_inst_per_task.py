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

import sys
import numpy
from detkit import get_instructions_per_task


# ======================
# test get inst per task
# ======================

def test_get_inst_per_task():
    """
    """

    # Insrructions for each task
    inst_per_matmat = get_instructions_per_task(task='matmat')
    inst_per_grammian = get_instructions_per_task(task='grammian')
    inst_per_cholesky = get_instructions_per_task(task='cholesky')
    inst_per_lu = get_instructions_per_task(task='lu')
    inst_per_lup = get_instructions_per_task(task='lup')

    # Instructions relative to matrix-matrix multiplication
    rel_inst_per_matmat = inst_per_matmat / inst_per_matmat
    rel_inst_per_grammian = inst_per_grammian / inst_per_matmat
    rel_inst_per_cholesky = inst_per_cholesky / inst_per_matmat
    rel_inst_per_lu = inst_per_lu / inst_per_matmat
    rel_inst_per_lup = inst_per_lup / inst_per_matmat

    # Print results
    print('instructions per matmat:   %0.3f, rel: %0.3f'
          % (inst_per_matmat, rel_inst_per_matmat))
    print('instructions per grammian: %0.3f, rel: %0.3f'
          % (inst_per_grammian, rel_inst_per_grammian))
    print('instructions per cholesky: %0.3f, rel: %0.3f'
          % (inst_per_cholesky, rel_inst_per_cholesky))
    print('instructions per lu:       %0.3f, rel: %0.3f'
          % (inst_per_lu, rel_inst_per_lu))
    print('instructions per lup:      %0.3f, rel: %0.3f'
          % (inst_per_lup, rel_inst_per_lup))


# ===========
# Script main
# ===========

if __name__ == "__main__":
    test_get_inst_per_task()
