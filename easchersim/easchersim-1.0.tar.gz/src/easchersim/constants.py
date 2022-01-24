# BSD 3-Clause License
#
# Copyright (c) 2021, Austin Cummings
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# todo alt_max should be user input

import numpy as np

# Constants to describe the atmospheric density profile as described by Linsley

# Maximum altitude of the atmosphere. Above this, density is 0g/cm^3
z_max = 112.79

# Layers of the atmosphere where the behavior changes (in km)
atmos_layer_boundaries = np.array([4, 10, 40, 100, z_max])

# Model parameters (b in g/cm^2, c in cm)
atmos_b = np.array([1222.6562, 1144.9069, 1305.5948, 540.1778, 1])
atmos_c = np.array([994186.38, 878153.55, 636143.04, 772170.16, 1e9])


# Avagadro's Constant (molecules/mol)
N_A = 6.022e23

# Average Molar Mass of Air (kg/mol)
mm_air = 28.9647e-3

# Average radius of the Earth (km)
R_Earth = 6378  # km

# Maximum altitude of the atmosphere to consider (km)
alt_max = 112.79

# Electron rest mass (MeV)
electron_mass = 0.511

# Electron charge (in Coulombs)
electron_charge = 1.602e-19

# Conversion factor between rest mass (in MeV/c^2) and kg
MeV_to_kg = 1.79E-30

# Fine structure constant
alpha_fsc = 1 / 137

# Speed of light (km/s)
cl = 3e5
