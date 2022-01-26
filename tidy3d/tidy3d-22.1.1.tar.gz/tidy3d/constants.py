import numpy as np

"""
This file contains constants that are used throghout the codebase.
"""

# Machine precision
dp_eps = np.finfo(np.float64).eps
fp_eps = np.finfo(np.float32).eps

# Very large value
inf = 1e20

# Data types to use
int_ = np.int32
float_ = np.float32
complex_ = np.complex64

# Values given to PEC and PMC for epsilon plotting
# If these are too small, the plotting breaks, but -1e6 is pretty small already
pec_viz = -1e6
pmc_viz = -3e6

# Value to use for PEC in the mode solver
pec_val = -1e8

# Physical constants. Base unit of length is micron.
EPSILON_0 = np.float32(8.85418782e-18)         # vacuum permittivity [F/um]
MU_0 = np.float32(1.25663706e-12)              # vacuum permeability [H/um]
C_0 = 1 / np.sqrt(EPSILON_0 * MU_0)            # speed of light in vacuum [um/s]
ETA_0 = np.sqrt(MU_0 / EPSILON_0)              # vacuum impedance
Q_e = 1.602176634e-19                          # funamental charge
HBAR = 6.582119569e-16                         # reduced Planck constant [eV*s]

# Conversion between 'x', 'y', 'z' and 0, 1, 2
xyz_dict = {'x': 0, 'y': 1, 'z': 2}
xyz_list = ['x', 'y', 'z']

