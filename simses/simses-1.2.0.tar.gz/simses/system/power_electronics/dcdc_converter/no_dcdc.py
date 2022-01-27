from simses.system.auxiliary.auxiliary import Auxiliary
from simses.system.power_electronics.dcdc_converter.abstract_dcdc_converter import DcDcConverter


class NoDcDcConverter(DcDcConverter):

    """
    This class acts like there is no DCDC converter included in the systems. It passes the voltage of the storage
    system to the intermediate circuit (which is in this case not an intermediate circuit anymore). Multiple parallel
    connected NoDcDcConverter produce invalid results.
    """

    __volumetric_power_density = 143 * 10 ** 6  # W / m3
    __GRAVIMETRIC_POWER_DENSITY = 11000  # W/kg
    __SPECIFIC_SURFACE_AREA = 0.0001  # in m2 / W  # TODO add exact values

    def __init__(self, intermediate_circuit_voltage: float):
        super(NoDcDcConverter, self).__init__(intermediate_circuit_voltage)
        self.__dc_power_loss: float = 0
        self.__dc_power: float = 0
        self.__dc_current: float = 0
        self.__dc_circuit_voltage: float = intermediate_circuit_voltage

    def calculate_dc_current(self, dc_power: float, storage_voltage: float) -> None:
        self.__dc_power = dc_power
        self.__dc_circuit_voltage = storage_voltage
        self.__dc_current = dc_power / storage_voltage

    def reverse_calculate_dc_current(self, dc_power: float, storage_voltage: float) -> None:
        self.__dc_power = dc_power
        self.__dc_circuit_voltage = storage_voltage
        self.__dc_current = dc_power / storage_voltage

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
    def intermediate_circuit_voltage(self) -> float:
        return self.__dc_circuit_voltage

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
