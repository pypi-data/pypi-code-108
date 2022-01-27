from simses.system.auxiliary.auxiliary import Auxiliary
from simses.system.power_electronics.dcdc_converter.abstract_dcdc_converter import DcDcConverter


class NoLossDcDcConverter(DcDcConverter):

    __volumetric_power_density = 143 * 10 ** 6  # W / m3
    __GRAVIMETRIC_POWER_DENSITY = 11000  # W/kg
    __SPECIFIC_SURFACE_AREA = 0.0001  # in m2 / W  # TODO add exact values

    # Exemplary value from:
    # (https://www.iisb.fraunhofer.de/en/research_areas/vehicle_electronics/dcdc_converters/High_Power_Density.html)

    def __init__(self, intermediate_circuit_voltage: float):
        super().__init__(intermediate_circuit_voltage)
        self.__dc_power_loss: float = 0
        self.__dc_power: float = 0
        self.__dc_current: float = 0

    def calculate_dc_current(self, dc_power: float, storage_voltage: float) -> None:
        self.__dc_power = dc_power
        self.__dc_current = dc_power / storage_voltage

    def reverse_calculate_dc_current(self, dc_power: float, storage_voltage: float) -> None:
        self.__dc_power = dc_power
        self.__dc_current = dc_power / self.intermediate_circuit_voltage

    @property
    def max_power(self) -> float:
        return 1e12

    @property
    def dc_power_loss(self):
        return self.__dc_power_loss

    @property
    def dc_power(self):
        return self.__dc_power

    @property
    def volume(self) -> float:
        # return self.max_power / self.__volumetric_power_density
        return 0

    @property
    def mass(self):
        return 0

    @property
    def surface_area(self) -> float:
        return 0

    @property
    def dc_current(self):
        return self.__dc_current

    def get_auxiliaries(self) -> [Auxiliary]:
        return list()

    def close(self) -> None:
        pass
