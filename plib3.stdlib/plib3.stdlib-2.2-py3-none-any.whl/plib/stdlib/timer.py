#!/usr/bin/env python3
"""
Module TIMER -- Code Timing Functions
Sub-Package STDLIB of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module provides functions for timing code, with
an alternate API to the standard library's ``timeit`` module
that is easier to use when timing functions that you already
have as objects, instead of source code strings.
"""

import sys
import itertools
import time
from contextlib import contextmanager


def _timeit(func, _it, _timer):
    # Only recent versions of the timeit module give you something like
    # this, and it's kind of unwieldy; it's easier just to crib this from
    # the timeit module's inner function and use it directly
    
    _t0 = _timer()
    _r = []
    for _i in _it:
        _f = func()
        _r.append(_f)
    _t1 = _timer()
    return _t1 - _t0, _r


# Cribbed from timeit module

if sys.platform == 'win32':
    default_timer = time.clock
else:
    default_timer = time.time


@contextmanager
def gcdisabled():
    # Cribbed from Timer.timeit method in timeit module; factored
    # out into context manager since it may be more generally useful
    import gc
    gcold = gc.isenabled()
    gc.disable()
    try:
        yield
    finally:
        if gcold:
            gc.enable()


def timeit(func, number=1000000):
    with gcdisabled():
        return _timeit(func, itertools.repeat(None, number), default_timer)


def repeat(func, repeat=3, number=1000000):
    # Cribbed from Timer.repeat method in timeit module
    tlist = []
    rlist = []
    for _ in range(repeat):
        t, r = timeit(func, number)
        tlist.append(t)
        rlist.append(r)
    return tlist, rlist
