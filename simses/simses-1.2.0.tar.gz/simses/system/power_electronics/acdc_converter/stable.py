import numpy as np

from simses.commons.log import Logger
from simses.commons.utils.utilities import check
from simses.system.power_electronics.acdc_converter.abstract_acdc_converter import AcDcConverter


class M2bAcDcConverter(AcDcConverter):
    """
    Efficiency curve of Modular Multilevel Battery Converter by mBee / STABL.
    Based on Master thesis of Markus Foerstl.

    Valid for a one-phase system with eight battery modules as described in:

    F\"orstl et al.
    "The Efficiency and Profitability of the Modular Multilevel Battery for Frequency Containment Reserve".
    In: 14th International Renewable Energy Storage Conference 2020 (IRES 2020), pp. 80-85
    doi: 10.2991/ahe.k.210202.012


    Functionality explained in
    Helling et al. "The AC lithium_ion –
    A novel approach for integrating batteries into AC systems" In: Electrical Power
    and Energy Systems 104 (2019) 150-158.
    DOI: 10.1016/j.ijepes.2018.06.047

    Inverter equation based on
    G.A. Rampinelli, A. Krenzinger, and F. Chenlo Romero.
    "Mathematical models for efficiency of inverters used in grid connected photovoltaic systems".
    In: Renewable and Sustainable Energy Reviews 34 (June 2014), pp. 578–587.
    doi: 10.1016/j.rser.2014.03.047.

    efficiency = p / (p + k0 + k1*p k2*p^2),
        where p = p_ac / p_max
    """

    # Rampinelli Fit
    __K0 = 0.003189
    __K1 = -0.007566
    __K2 = 0.009991

    __VOLUMETRIC_POWER_DENSITY = 143 * 1e6  # W / m3
    __GRAVIMETRIC_POWER_DENSITY = 17000  # W/kg
    __SPECIFIC_SURFACE_AREA = 0.0001  # in m2 / W  # TODO add exact values
    # Exemplary value from:
    # (https://www.iisb.fraunhofer.de/en/research_areas/vehicle_electronics/dcdc_converters/High_Power_Density.html)
    # ( https://www.apcuk.co.uk/app/uploads/2018/02/PE_Full_Pack.pdf )

    def __init__(self, max_power: float):
        super().__init__(max_power)
        self.__log: Logger = Logger(type(self).__name__)

    def to_ac(self, power: float, voltage: float) -> float:
        check(power)
        res: float = 0.0
        if power < 0.0:
            res = power / self.__get_efficiency(power)
        return res

    def to_dc(self, power: float, voltage: float) -> float:
        check(power)
        res: float = 0.0
        if power > 0.0:
            res = power * self.__get_efficiency(power)
        return res

    def to_dc_reverse(self, dc_power: float, voltage: float) -> float:
        check(dc_power)
        res: float = 0.0
        if dc_power > 0.0:
            p = (abs(dc_power) * self.max_power * (1 + self.__K1)) / (self.__K2 * abs(dc_power) - self.max_power)
            q = (abs(dc_power) * self.__K0 * self.max_power ** 2) / (self.__K2 * abs(dc_power) - self.max_power)
            res = max(0.0, -p / 2 + np.sqrt((p / 2) ** 2 - q))
        return res

    def to_ac_reverse(self, dc_power: float, voltage: float) -> float:
        check(dc_power)
        res: float = 0.0
        if dc_power < 0.0:
            p = (self.max_power + self.__K1 * self.max_power) / self.__K2
            q = (self.max_power ** 2 * self.__K0 - abs(dc_power) * self.max_power) / self.__K2
            res = min(0.0, -(-p / 2 + np.sqrt((p / 2) ** 2 - q)))
        return res

    def __get_efficiency(self, power: float) -> float:
        power_ratio = abs(power) / self.max_power
        if power_ratio < 0.0 or power_ratio > 1.0:
            raise Exception('Power ratio is not possible: ' + str(power_ratio))
        return power_ratio / (power_ratio + self.__K0 + self.__K1 * power_ratio + self.__K2 * power_ratio**2)

    @property
    def volume(self) -> float:
        return self.max_power / self.__VOLUMETRIC_POWER_DENSITY

    @property
    def mass(self):
        return self.max_power / self.__GRAVIMETRIC_POWER_DENSITY

    @property
    def surface_area(self) -> float:
        return self.max_power * self.__SPECIFIC_SURFACE_AREA

    @classmethod
    def create_instance(cls, max_power: float, power_electronics_config=None):
        return M2bAcDcConverter(max_power)

    def close(self) -> None:
        self.__log.close()
