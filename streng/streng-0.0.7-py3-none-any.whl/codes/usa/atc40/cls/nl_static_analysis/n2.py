from dataclasses import dataclass, field
from typing import List
import numpy as np
from ...raw.ch8 import csm as csm_atc40
from ......common.math.numerical import intersection
from ......common.io.output import OutputTable, OutputExtended
from ......tools.bilin import Bilin, BilinearCurve
from ......codes.eurocodes.ec8.cls.seismic_action import spectra as spec_ec8



@dataclass
class StructureProperties:
    φ: np.ndarray
    m: np.ndarray
    T0: float
    pushover_curve_F: np.ndarray
    pushover_curve_δ: np.ndarray

    def __post_init__(self):
        self.PF1 = csm_atc40.PF1(self.m, self.φ)
        self.α1 = csm_atc40.α1(self.m, self.φ)
        self.φroof1 = self.φ[-1]
        self.Sa = csm_atc40.Sa(V=self.pushover_curve_F,
                               W=sum(self.m),
                               α1=self.α1)
        self.Sd = csm_atc40.Sd(Δroof=self.pushover_curve_δ,
                               PF1=self.PF1,
                               φroof1=self.φroof1)


@dataclass
class Demand:
    T_range: np.ndarray
    Sa: np.ndarray
    Sd: np.ndarray
    TC: float

    def ec8_elastic(self, αgR: float, γI: float, ground_type: str, spectrum_type: int, η=1.0, q=1.0, β=0.2):
        _spec_ec8 = spec_ec8.SpectraEc8(αgR, γI, ground_type, spectrum_type, η, q, β)
        self.Sa = _spec_ec8.Se(self.T_range)
        self.Sd = _spec_ec8.SDe(self.T_range)
        self.TC = _spec_ec8.TC


@dataclass
class N2Method:
    structure: StructureProperties
    demand: Demand

    def __post_init__(self):
        self.output = OutputTable()

    @staticmethod
    def Rμ(μ, T, TC):
        if T < TC:
            return (μ-1)*(T/TC) + 1.0
        else:
            return μ

    @staticmethod
    def Sa(_Sae, _Rμ):
        return _Sae/_Rμ

    @staticmethod
    def Sd(_Sde, _μ, _Rμ):
        return (_μ/_Rμ) * _Sde

    def Sa_for_μ(self, μ):
        _rm = np.array([self.Rμ(μ, t, self.demand.TC) for t in self.demand.T_range])
        _sa = self.demand.Sa / _rm
        return _sa

    def Sd_for_μ(self, μ):
        _rm = np.array([self.Rμ(μ, t, self.demand.TC) for t in self.demand.T_range])
        _sd = self.Sd(self.demand.Sd, μ, _rm)
        return _sd

