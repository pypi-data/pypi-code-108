from mudpy.containers import mdict
import numpy as np

# Dictinary of nuclear lifetimes for nuclei of interest as β-NMR probes.
# Orginally adapted from the compilation in slr_v2.cpp (by R. M. L. McFadden).
# All reported values are in seconds.
# See also: https://www-nds.iaea.org/relnsd/vcharthtml/VChartHTML.html
life = mdict(
    {
        # Lithium-8
        # https://doi.org/10.1103/PhysRevC.82.027309
        "Li8": 0.83840 / np.log(2),
        "Li8_err": 0.00036 / np.log(2),
        # Lithium-9
        # https://doi.org//10.1103/PhysRevC.13.835
        "Li9": 0.1783 / np.log(2),
        "Li9_err": 0.0004 / np.log(2),
        # Lithium-11
        # https://doi.org/10.1016/j.nuclphysa.2012.01.010
        "Li11": 0.00875 / np.log(2),
        "Li11_err": 0.00014 / np.log(2),
        # Beryllium-11
        # https://doi.org/10.1016/j.nuclphysa.2012.01.010
        "Be11": 13.76 / np.log(2),
        "Be11_err": 0.07 / np.log(2),
        # Fluorine-20
        # https://doi.org/10.1103/PhysRevC.99.015501
        "F20": 11.0062 / np.log(2),
        "F20_err": 0.00080 / np.log(2),
        # Sodium-26
        # https://doi.org/10.1016/j.nds.2016.04.001
        "Na26": 1.07128 / np.log(2),
        "Na26_err": 0.00025 / np.log(2),
        # Magnesium-29
        # https://doi.org/10.1016/j.nds.2012.04.001
        "Mg29": 1.30 / np.log(2),
        "Mg29_err": 0.12 / np.log(2),
        # Magnesium-31
        # https://doi.org/10.1016/j.nds.2013.03.001
        "Mg31": 0.236 / np.log(2),
        "Mg31_err": 0.020 / np.log(2),
        # Magnesium-33
        # https://doi.org/10.1016/j.nds.2011.04.003
        "Mg33": 0.0905 / np.log(2),
        "Mg33_err": 0.0016 / np.log(2),
        # Actinium-230
        # https://doi.org/10.1016/j.nds.2012.08.002
        "Ac230": 122 / np.log(2),
        "Ac230_err": 3 / np.log(2),
        # Actinium-232
        # https://doi.org/10.1016/j.nds.2006.09.001
        "Ac232": 119 / np.log(2),
        "Ac232_err": 5 / np.log(2),
        # Actinium-234
        # https://doi.org/10.1016/j.nds.2007.02.003
        "Ac234": 44 / np.log(2),
        "Ac234_err": 7 / np.log(2),
    }
)
