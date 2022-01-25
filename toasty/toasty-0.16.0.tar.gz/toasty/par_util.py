# -*- mode: python; coding: utf-8 -*-
# Copyright 2020 the AAS WorldWide Telescope project
# Licensed under the MIT License.

"""Utilities for parallel processing

"""
from __future__ import absolute_import, division, print_function

__all__ = '''
SHOW_INFORMATIONAL_MESSAGES
resolve_parallelism
'''.split()

import multiprocessing as mp
import os
import sys

SHOW_INFORMATIONAL_MESSAGES = True

def resolve_parallelism(parallel):
    """Decide what level of parallelism to use.

    Parameters
    ----------
    parallel : integer or None
        The user's specification

    Returns
    -------
    A positive integer giving the parallelization level.

    """
    if parallel is None:
        if mp.get_start_method() == 'fork':
            parallel = os.cpu_count()
            if SHOW_INFORMATIONAL_MESSAGES and parallel > 1:
                print(f'info: parallelizing processing over {parallel} CPUs')
        else:
            parallel = 1

    if parallel > 1 and mp.get_start_method() != 'fork':
        print('''warning: parallel processing was requested but is not possible
    because this operating system is not using `fork`-based multiprocessing
    On macOS a bug prevents forking: https://bugs.python.org/issue33725''', file=sys.stderr)
        parallel = 1

    if parallel > 1:
        return parallel

    return 1
