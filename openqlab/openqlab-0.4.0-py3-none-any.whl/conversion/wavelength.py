import warnings

import openqlab.analysis.electromagnetic_wave
from openqlab.analysis.electromagnetic_wave import ElectromagneticWave


def Wavelength(lambda0: float) -> ElectromagneticWave:
    warnings.warn(
        f"Class Wavelength is deprecated! Use {openqlab.analysis.electromagnetic_wave.ElectromagneticWave} instead.",
        DeprecationWarning,
    )
    return openqlab.analysis.electromagnetic_wave.ElectromagneticWave(lambda0)
