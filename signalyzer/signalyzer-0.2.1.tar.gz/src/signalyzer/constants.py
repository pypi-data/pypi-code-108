# -*- coding: utf-8 -*-
"""
constants.py
~~~~~~~~~~~~
Constants.

:copyright: (c) 2021 by Jochen Gerhaeusser.
:license: BSD, see LICENSE for details
"""

import numpy as np

#: Maximal value for a 32-bit floating point number
f32_MAX: float = (1 - 2 ** -24) * 2 ** 128

#: Maximal value for a cubic 32-bit floating point number
f32_MAX_POW3 = np.cbrt(f32_MAX)

#: Minimal de-normalized value for a floating-point number
f32_MIN: float = 2 ** -149

#: Minimal normalized value for a floating-point number
f32_MIN_POSITIVE: float = 2 ** -126

#: Epsilon value for a 32-bit floating-point number
f32_EPSILON: float = 2 ** -24
