# -*- coding: utf-8 -*-
"""
signalyzer.py
~~~~~~~~~~~~~
Public package API.

:copyright: (c) 2021-2022 by Jochen Gerhaeusser.
:license: BSD, see LICENSE for details.
"""

from .trace import *
from .statemachine import *

# package exports
__all__ = [
    # Representations
    'Point2D', 'Vector',
    'Point3D',
    'State2D', 'State3D',

    # Signal Processing
    'Statistics',
    'SlewRateLimiter',
    'ExponentialSmoothing',
    'LinearRegression',
    'IIRFilter',

    # State Machines
    'Statemachine',

    # Traces
    'Trace', 'vectorize',
    'Traces', 'as_traces',
    'VectorTraces', 'polar',
    'StatisticsTraces',
    'MovingAverageTraces',
    'SetTraces', 'combine',
    'SlewRateLimiterTraces',
    'ExponentialSmoothingTraces',
    'LinearRegressionTraces',

]

__version__ = '0.2.1'

