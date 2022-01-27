#!/usr/bin/env python
# Copyright 2020-2022 The PyFLOSIC Developers. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Sebastian Schwalbe <theonov13@gmail.com>

import numpy 

#
# Reference: 
#   - https://github.com/charnley/rmsd/blob/master/rmsd/calculate_rmsd.py
# Purpose: 
#   - symmetry.py inertia tensor
atomic_masses = {
    1: 1.00797,
    2: 4.00260,
    3: 6.941,
    4: 9.01218,
    5: 10.81,
    6: 12.011,
    7: 14.0067,
    8: 15.9994,
    9: 18.998403,
    10: 20.179,
    11: 22.98977,
    12: 24.305,
    13: 26.98154,
    14: 28.0855,
    15: 30.97376,
    16: 32.06,
    17: 35.453,
    19: 39.0983,
    18: 39.948,
    20: 40.08,
    21: 44.9559,
    22: 47.90,
    23: 50.9415,
    24: 51.996,
    25: 54.9380,
    26: 55.847,
    28: 58.70,
    27: 58.9332,
    29: 63.546,
    30: 65.38,
    31: 69.72,
    32: 72.59,
    33: 74.9216,
    34: 78.96,
    35: 79.904,
    36: 83.80,
    37: 85.4678,
    38: 87.62,
    39: 88.9059,
    40: 91.22,
    41: 92.9064,
    42: 95.94,
    43: 98,
    44: 101.07,
    45: 102.9055,
    46: 106.4,
    47: 107.868,
    48: 112.41,
    49: 114.82,
    50: 118.69,
    51: 121.75,
    53: 126.9045,
    52: 127.60,
    54: 131.30,
    55: 132.9054,
    56: 137.33,
    57: 138.9055,
    58: 140.12,
    59: 140.9077,
    60: 144.24,
    61: 145,
    62: 150.4,
    63: 151.96,
    64: 157.25,
    65: 158.9254,
    66: 162.50,
    67: 164.9304,
    68: 167.26,
    69: 168.9342,
    70: 173.04,
    71: 174.967,
    72: 178.49,
    73: 180.9479,
    74: 183.85,
    75: 186.207,
    76: 190.2,
    77: 192.22,
    78: 195.09,
    79: 196.9665,
    80: 200.59,
    81: 204.37,
    82: 207.2,
    83: 208.9804,
    84: 209,
    85: 210,
    86: 222,
    87: 223,
    88: 226.0254,
    89: 227.0278,
    91: 231.0359,
    90: 232.0381,
    93: 237.0482,
    92: 238.029,
    94: 242,
    95: 243,
    97: 247,
    96: 247,
    102: 250,
    98: 251,
    99: 252,
    108: 255,
    109: 256,
    100: 257,
    101: 258,
    103: 260,
    104: 261,
    107: 262,
    105: 262,
    106: 263,
    110: 269,
    111: 272,
    112: 277,
}

#  Covalent radii 
#  --------------
#
#  Reference
#  ---------
#   - [1] ase.data: Covalent radii revisited,
#         Beatriz Cordero, Verónica Gómez, Ana E. Platero-Prats, Marc Revés,
#         Jorge Echeverría, Eduard Cremades, Flavia Barragán and Santiago Alvarez,
#         Dalton Trans., 2008, 2832-2838 DOI:10.1039/B801115J
# Notes
# ----- 
#   - needed by
#       + get_guess_bond_order
missing = 0.2
covalent_radii = numpy.array([
    missing,  # X
    0.31,  # H
    0.28,  # He
    1.28,  # Li
    0.96,  # Be
    0.84,  # B
    0.76,  # C
    0.71,  # N
    0.66,  # O
    0.57,  # F
    0.58,  # Ne
    1.66,  # Na
    1.41,  # Mg
    1.21,  # Al
    1.11,  # Si
    1.07,  # P
    1.05,  # S
    1.02,  # Cl
    1.06,  # Ar
    2.03,  # K
    1.76,  # Ca
    1.70,  # Sc
    1.60,  # Ti
    1.53,  # V
    1.39,  # Cr
    1.39,  # Mn
    1.32,  # Fe
    1.26,  # Co
    1.24,  # Ni
    1.32,  # Cu
    1.22,  # Zn
    1.22,  # Ga
    1.20,  # Ge
    1.19,  # As
    1.20,  # Se
    1.20,  # Br
    1.16,  # Kr
    2.20,  # Rb
    1.95,  # Sr
    1.90,  # Y
    1.75,  # Zr
    1.64,  # Nb
    1.54,  # Mo
    1.47,  # Tc
    1.46,  # Ru
    1.42,  # Rh
    1.39,  # Pd
    1.45,  # Ag
    1.44,  # Cd
    1.42,  # In
    1.39,  # Sn
    1.39,  # Sb
    1.38,  # Te
    1.39,  # I
    1.40,  # Xe
    2.44,  # Cs
    2.15,  # Ba
    2.07,  # La
    2.04,  # Ce
    2.03,  # Pr
    2.01,  # Nd
    1.99,  # Pm
    1.98,  # Sm
    1.98,  # Eu
    1.96,  # Gd
    1.94,  # Tb
    1.92,  # Dy
    1.92,  # Ho
    1.89,  # Er
    1.90,  # Tm
    1.87,  # Yb
    1.87,  # Lu
    1.75,  # Hf
    1.70,  # Ta
    1.62,  # W
    1.51,  # Re
    1.44,  # Os
    1.41,  # Ir
    1.36,  # Pt
    1.36,  # Au
    1.32,  # Hg
    1.45,  # Tl
    1.46,  # Pb
    1.48,  # Bi
    1.40,  # Po
    1.50,  # At
    1.50,  # Rn
    2.60,  # Fr
    2.21,  # Ra
    2.15,  # Ac
    2.06,  # Th
    2.00,  # Pa
    1.96,  # U
    1.90,  # Np
    1.87,  # Pu
    1.80,  # Am
    1.69,  # Cm
    missing,  # Bk
    missing,  # Cf
    missing,  # Es
    missing,  # Fm
    missing,  # Md
    missing,  # No
    missing,  # Lr
    missing,  # Rf
    missing,  # Db
    missing,  # Sg
    missing,  # Bh
    missing,  # Hs
    missing,  # Mt
    missing,  # Ds
    missing,  # Rg
    missing,  # Cn
    missing,  # Nh
    missing,  # Fl
    missing,  # Mc
    missing,  # Lv
    missing,  # Ts
    missing,  # Og
])

