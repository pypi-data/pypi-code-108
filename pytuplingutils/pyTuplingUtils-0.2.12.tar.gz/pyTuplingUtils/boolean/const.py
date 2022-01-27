#!/usr/bin/env python3
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Thu Jul 30, 2020 at 04:03 AM +0800

import numpy as np


KNOWN_SYMB = {
    # Mathematical constants
    'pi': np.pi,
    'e': np.e,
    # Units
    'MeV': 1.0,
    'GeV': 1000.0,
    # Particle masses
    # B mesons
    'PDG_M_B0': 5279.64,
    # D mesons
    'PDG_M_Dst': 2010.26,
    'PDG_M_D0': 1864.83,
}

KNOWN_FUNC = {
    # NOTE: Convention is lowercase for functions that ROOT can parse, and uppercase otherwise
    'abs': np.abs,
    'log': np.log,
    'sin': np.sin,
    'ONE': lambda: 1,
    'LOG10pp': lambda p1x, p1y, p1z, p2x, p2y, p2z: np.log10(1-(p1x*p2x + p1y*p2y + p1z*p2z)/np.sqrt(p1x*p1x+p1y*p1y+p1z*p1z)/np.sqrt(p2x*p2x+p2y*p2y+p2z*p2z)),
    'ETA': lambda p, pz: np.log((p+pz)/(p-pz))/2.,
    'NORM2': lambda x, y: np.sqrt(x*x + y*y),
    'GT': lambda x, y: x > y,
    'LT': lambda x, y: x < y,
}
