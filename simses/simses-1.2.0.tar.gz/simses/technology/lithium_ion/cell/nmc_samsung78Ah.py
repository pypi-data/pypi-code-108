from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.electric.properties import ElectricalCellProperties
from simses.technology.lithium_ion.cell.format.abstract import CellFormat
from simses.technology.lithium_ion.cell.format.prismatic import PrismaticCell
from simses.technology.lithium_ion.cell.thermal.properties import ThermalCellProperties
from simses.technology.lithium_ion.cell.type import CellType


class Samsung78AhNMC(CellType):
    """Characterisation using field data: Master Thesis by Felix Müller"""

    r""" Source:
        Field data from fcr storage system. Datasheet can be found here:
        ...\simses\simulation\storage_system\technology\lithium_ion\cell_type\data\nmc_samsung78Ah_datasheet.pdf
    """

    __CELL_VOLTAGE = 3.7  # V
    __CELL_CAPACITY = 73.95  # Ah
    __CELL_RESISTANCE = 0.636847061 * 10 ** (-3)  # Ohm
    __MAX_VOLTAGE: float = 4.1  # V
    __MIN_VOLTAGE: float = 2.7  # V
    __MIN_TEMPERATURE: float = 248.15  # K
    __MAX_TEMPERATURE: float = 323.15  # K
    __MAX_CHARGE_RATE: float = 2.0  # 1/h
    __MAX_DISCHARGE_RATE: float = 4.0  # 1/h
    __SELF_DISCHARGE_RATE: float = 0.0  # X.X%-soc per day, e.g., 0.015 for 1.5% SOC loss per day
    __MASS: float = 2.0  # kg per cell
    __SPECIFIC_HEAT: float = 823  # J/kgK
    __CONVECTION_COEFFICIENT: float = 15  # W/m2K

    __COULOMB_EFFICIENCY: float = 0.9843  # p.u.

    # Values from nmc_sanyo_ur18650e (source: https://akkuplus.de/Panasonic-UR18650E-37-Volt-2150mAh-Li-Ion-EOL)

    __HEIGHT: float = 125.7  # mm
    __WIDTH: float = 45.6  # mm
    __LENGTH: float = 173.9  # mm

    __ELECTRICAL_PROPS: ElectricalCellProperties = ElectricalCellProperties(__CELL_VOLTAGE, __CELL_CAPACITY,
                                                                            __MIN_VOLTAGE, __MAX_VOLTAGE,
                                                                            __MAX_CHARGE_RATE, __MAX_DISCHARGE_RATE,
                                                                            __SELF_DISCHARGE_RATE, __COULOMB_EFFICIENCY)
    __THERMAL_PROPS: ThermalCellProperties = ThermalCellProperties(__MIN_TEMPERATURE, __MAX_TEMPERATURE, __MASS,
                                                                   __SPECIFIC_HEAT, __CONVECTION_COEFFICIENT)
    __CELL_FORMAT: CellFormat = PrismaticCell(__HEIGHT, __WIDTH, __LENGTH)

    # Parameters for Curve Fitting: Discharge
    __p1_dch = 20.290042045
    __p2_dch = -60.088705239
    __p3_dch = 65.004615460
    __p4_dch = -30.204504426
    __p5_dch = 5.208737944
    __p6_dch = 0.473682851
    __p7_dch = 3.394776910

    # Parameters for Curve Fitting: Charge
    __p1_ch = 20.717822026
    __p2_ch = -60.174639133
    __p3_ch = 62.332299803
    __p4_ch = -25.900465062
    __p5_ch = 2.767903886
    __p6_ch = 0.931931308
    __p7_ch = 3.408247703

    # Parameters for Curve Fitting: Rest
    __p1_rest = 5.255925680
    __p2_rest = -14.288201873
    __p3_rest = 11.785819139
    __p4_rest = -0.932995895
    __p5_rest = -2.416565204
    __p6_rest = 1.282337714
    __p7_rest = 3.375062956

    def __init__(self, voltage: float, capacity: float, soh: float, battery_config: BatteryConfig):
        super().__init__(voltage, capacity, soh, self.__ELECTRICAL_PROPS, self.__THERMAL_PROPS, self.__CELL_FORMAT,
                         battery_config)
        self.__log: Logger = Logger(type(self).__name__)

    def get_open_circuit_voltage(self, battery_state: LithiumIonState) -> float:
        soc = battery_state.soc
        if battery_state.is_charge:
            open_circuit_voltage_cell = self.__p1_ch * soc ** 6 + self.__p2_ch * soc ** 5 + self.__p3_ch * soc ** 4 + \
                                        self.__p4_ch * soc ** 3 + self.__p5_ch * soc ** 2 + self.__p6_ch * soc + self.__p7_ch
        else:
            if battery_state.current == 0:
                open_circuit_voltage_cell = self.__p1_rest * soc ** 6 + self.__p2_rest * soc ** 5 + self.__p3_rest * soc ** 4 + \
                                            self.__p4_rest * soc ** 3 + self.__p5_rest * soc ** 2 + self.__p6_rest * soc + self.__p7_rest
            else:
                open_circuit_voltage_cell = self.__p1_dch * soc ** 6 + self.__p2_dch * soc ** 5 + self.__p3_dch * soc ** 4 + \
                                            self.__p4_dch * soc ** 3 + self.__p5_dch * soc ** 2 + self.__p6_dch * soc + self.__p7_dch
        return open_circuit_voltage_cell * self.get_serial_scale()

    def get_internal_resistance(self, battery_state: LithiumIonState) -> float:
        return float(self.__CELL_RESISTANCE / self.get_parallel_scale() * self.get_serial_scale())

    def close(self):
        self.__log.close()
