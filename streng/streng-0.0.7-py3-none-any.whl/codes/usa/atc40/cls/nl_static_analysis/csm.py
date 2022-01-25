from dataclasses import dataclass, field
from typing import List
import numpy as np
from ......codes.usa.atc40.raw.ch8 import csm as csm_atc40
# from ...raw.ch8 import csm as csm_atc40
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
    behavior: str

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
class CapacitySpectrumMethod:
    structure: StructureProperties
    demand: Demand
    first_try_case: str = 'intersection'

    def __post_init__(self):
        self.output = OutputTable()

    @property
    def Sd_first_try(self):
        if self.first_try_case == 'intersection':
            x_solve, y_solve = intersection(self.demand.Sd, self.demand.Sa, self.structure.Sd, self.structure.Sa)
            return x_solve[-1]
        elif self.first_try_case == 'equal displacements':
            Sd_T0 = 100.
            Sa_T0 = Sd_T0 * (2 * np.pi / self.structure.T0) ** 2
            Sa_T0_array = np.array([0.0, Sa_T0])
            Sd_T0_array = np.array([0.0, Sd_T0])
            xT0_solve, yT0_solve = intersection(self.demand.Sd, self.demand.Sa, Sd_T0_array, Sa_T0_array)
            return xT0_solve[-1]
        else:
            return 0.

    def __iterate_SR(self, x0):
        bl = Bilin(xtarget=x0)
        bl.curve_ini.x, bl.curve_ini.y = self.structure.Sd, self.structure.Sa
        bl.calc()

        β0 = bl.bilinear_curve.β0
        βeff = csm_atc40.βeff(0.05, β0, self.structure.behavior)

        Teff = bl.bilinear_curve.Teq(self.structure.T0)


        SRA = csm_atc40.SRA(βeff, self.structure.behavior)
        SRV = csm_atc40.SRV(βeff, self.structure.behavior)

        if Teff > self.demand.TC:
            SR = SRV
        else:
            SR = SRA

        _Sa = SR * self.demand.Sa
        _Sd = SR * self.demand.Sd

        x_solve, y_solve = intersection(_Sd, _Sa, self.structure.Sd, self.structure.Sa)
        return x_solve[-1]

    def calc_performance_point(self):
        # self.output.log_table.dict_list.clear()
        x_i = self.Sd_first_try
        iter_num = 0
        error = 100.
        self.output.data.clear()
        self.output.data.append({'__iteration': iter_num, 'Sd': x_i, 'error': None})
        while error > 0.0001:
            x_new = self.__iterate_SR(x_i)
            error = abs((x_new - x_i) / x_i)
            x_i = x_new
            iter_num = iter_num + 1

            self.output.data.append({'__iteration': iter_num, 'Sd': x_i, 'error': error})

            # print(f'__iteration: {iter_num} x={x_i:.4f} error={error:.2%}')


        print(f'solution: Sd = {x_i:.4f}m')


@dataclass
class CapacitySpectrumMethodProcedureB:
    """
    incomplete...check jupyter notebook
    """
    structure: StructureProperties
    demands: List[Demand] = field(default_factory=list)
    dstar: float = None
    astar: float = None
    bilinear_curve: BilinearCurve = None


    def __post_init__(self):
        self.output = OutputTable()

    def calc_performance_point(self):
        self.dstar_intersection = self._get_dstar()
        self.bilinear_curve = self._get_bilinear_curve()
        self.astar = self.bilinear_curve.au
        self._try_more_points()




    def _get_dstar(self):
        bl = Bilin()
        bl.curve_ini.x = self.structure.Sd
        bl.curve_ini.y = self.structure.Sa
        bl.calc()

        kel = bl.bilinear_curve.kel
        x_kel = np.array([0., 10.])
        y_kel = np.array([0., 10. * kel])

        _dstar, _adstar = intersection(x_kel, y_kel, self.demands[0]['demand'].Sd, self.demands[0]['demand'].Sa)
        self.dstar = _dstar[0]

        return _dstar[0], _adstar[0]


    def _get_bilinear_curve(self):
        bl = Bilin(xtarget=self.dstar)
        bl.curve_ini.x = self.structure.Sd
        bl.curve_ini.y = self.structure.Sa
        bl.calc()
        return bl.bilinear_curve

    def _try_more_points(self):
        self.dpi_rng = np.linspace(0.5 * self.dstar, 1.5 * self.dstar, 11)
        self.api_rng = self._api(self.astar, self.dstar, self.bilinear_curve.ay, self.bilinear_curve.dy, self.dpi_rng)
        self.β0_rng = csm_atc40.β0(self.bilinear_curve.dy, self.bilinear_curve.ay, self.dpi_rng, self.api_rng)
        self.βeff_rng = np.array([csm_atc40.βeff(0.05, x, self.structure.behavior) for x in  self.β0_rng])




    @staticmethod
    def _api(astar, dstar, ay, dy, dpi):
        return ay + (astar - ay) * (dpi - dy) / (dstar - dy)


