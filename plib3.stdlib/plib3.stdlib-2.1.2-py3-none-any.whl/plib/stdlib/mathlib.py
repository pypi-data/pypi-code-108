#!/usr/bin/env python3
"""
Module MATHLIB -- Math Library Functions
Sub-Package STDLIB of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module supplements the ``math`` module in the Python
standard library. It currently contains the following:

function gcd -- fast implementation of Euclid's GCD algorithm.

function lcm -- fast implementation of LCM based on GCD above.
"""


def gcd(x, y):
    """Return greatest common divisor of x, y.
    """
    while x:
        x, y = y % x, x
    return y


def lcm(x, y):
    """Return least common multiple of x, y.
    """
    if (x == 0) or (y == 0):
        return 0
    return x * y // gcd(x, y)
