import numpy as np

from simses.commons.log import Logger
from simses.commons.utils.utilities import check
from simses.system.power_electronics.acdc_converter.abstract_acdc_converter import AcDcConverter


class NottonLossAcDcConverter(AcDcConverter):

    # Notton Type 2 inverter
    __P0 = 0.0072
    __K = 0.0345

    __VOLUMETRIC_POWER_DENSITY = 143 * 1e6  # W / m3
    __GRAVIMETRIC_POWER_DENSITY = 17000  # W/kg
    __SPECIFIC_SURFACE_AREA = 0.0001  # in m2 / W  # TODO add exact values
    # Exemplary value from:
    # (https://www.iisb.fraunhofer.de/en/research_areas/vehicle_electronics/dcdc_converters/High_Power_Density.html)
    # ( https://www.apcuk.co.uk/app/uploads/2018/02/PE_Full_Pack.pdf )

    def __init__(self, max_power):
        super().__init__(max_power)
        self.__log: Logger = Logger(type(self).__name__)

    def to_ac(self, power: float, voltage: float) -> float:
        check(power)
        res: float = 0.0
        if power < 0.0:
            res = min(power - self.__get_loss(power), 0)
        return res

    def to_dc(self, power: float, voltage: float) -> float:
        check(power)
        res: float = 0.0
        if power > 0.0:
            res = max(power - self.__get_loss(power), 0)
        return res

    def to_dc_reverse(self, dc_power: float, voltage: float) -> float:
        check(dc_power)
        res: float = 0.0
        if dc_power > 0.0:
            p = - dc_power / (1 - dc_power * self.__K / self.max_power)
            q = - self.__P0 * dc_power / (1 / self.max_power - abs(dc_power) * self.__K / self.max_power ** 2)
            res = max(0.0, -p / 2 + np.sqrt((p / 2) ** 2 - q))
        return res

    def to_ac_reverse(self, dc_power: float, voltage: float) -> float:
        check(dc_power)
        res: float = 0.0
        if dc_power < 0.0:
            p = self.max_power / self.__K
            q = (self.__P0 * self.max_power ** 2 - abs(dc_power) * self.max_power) / self.__K
            self.__log.debug('P_DC: ' + str(dc_power))
            res = min(0.0, -(-p / 2 + np.sqrt((p / 2) ** 2 - q)))
        return res

    def __get_loss(self, power: float) -> float:
        return abs(self.__P0 * self.max_power + (self.__K / self.max_power) * power ** 2)

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
        return NottonLossAcDcConverter(max_power)

    def close(self) -> None:
        pass
