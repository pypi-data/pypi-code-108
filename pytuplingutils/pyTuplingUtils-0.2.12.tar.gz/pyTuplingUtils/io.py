#!/usr/bin/env python3
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Sun May 09, 2021 at 02:52 AM +0200

import numpy as np

ARRAY_TYPE = 'np'


def read_branch(ntp, tree, branch, idx=None):
    data = ntp[tree][branch].array(library=ARRAY_TYPE)

    return data if not idx else data[idx]


def read_branches_dict(ntp, tree, branches):
    return ntp[tree].arrays(branches, library=ARRAY_TYPE)


def read_branches(ntp, tree, branches, idx=None, transpose=False):
    data = list(ntp[tree].arrays(branches, library=ARRAY_TYPE).values())

    if idx is not None:
        data = [d[idx] for d in data]

    return np.column_stack(data) if transpose else data
