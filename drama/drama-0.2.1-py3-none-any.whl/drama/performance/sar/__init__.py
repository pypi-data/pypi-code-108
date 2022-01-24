"""
=======================================================
SAR Performance Package (:mod:`drama.performance.sar`)
=======================================================
"""

from drama.performance.sar.antenna_patterns import (
    sinc_bp,
    sinc_1tx_nrx,
    pattern,
    phased_spacedarray,
)

# from drama.performance.sar.simulators import pointSim, back_project
from drama.performance.sar.data_patch import find_patch, pt_connect
from drama.performance.sar.azimuth_performance import (
    calc_aasr,
    calc_nesz,
    AASRdata,
    NESZdata,
)
from drama.performance.sar.range_ambiguities import RASR, RASRdata
from drama.performance.sar.mode_cfg import SARModeFromCfg
