import pandas as pd
import scipy.interpolate

from simses.commons.config.data.battery import BatteryDataConfig
from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.electric.properties import ElectricalCellProperties
from simses.technology.lithium_ion.cell.format.abstract import CellFormat
from simses.technology.lithium_ion.cell.format.prismatic import PrismaticCell
from simses.technology.lithium_ion.cell.thermal.default import DefaultThermalCellProperties
from simses.technology.lithium_ion.cell.thermal.properties import ThermalCellProperties
from simses.technology.lithium_ion.cell.type import CellType


class SodiumIonGreenRock(CellType):
    # Anode: NaTi2(PO4)3
    # Cathode: : LiMn2O4
    # Electrolyte: Na2SO4-based
    # Separator:
    # current collector: stainless steel
    # at 40°C (= 313,15 K)

    __SOC_HEADER = 'SOC'
    __SOC_IDX = 0
    __OCV_IDX = 1
    __RINT_Ch_IDX = 1
    __RINT_Dch_IDX = 2
    #__SOC_CH_IDX = 0
    #__SOC_DCH_IDX = 2
    #__OCV_CH_IDX = 1
    #__OCV_DCH_IDX = 3

    __CELL_VOLTAGE = 1.5  # V
    __CELL_CAPACITY = 28  # Ah
    __MAX_VOLTAGE: float = 1.9  # V
    __MIN_VOLTAGE: float = 0.8  # V
    __MAX_CHARGE_RATE: float = 0.33  # 1/h
    __MAX_DISCHARGE_RATE: float = 0.33  # 1/h
    __SELF_DISCHARGE_RATE: float = 0.0  # unknown

    __HEIGHT: float = 50  # mm
    __WIDTH: float = 100  # mm
    __LENGTH: float = 200  # mm

    __CELL_FORMAT: CellFormat = PrismaticCell(__HEIGHT, __WIDTH, __LENGTH)

    __COULOMB_EFFICIENCY: float = 1.0  # p.u

    __ELECTRICAL_PROPS: ElectricalCellProperties = ElectricalCellProperties(__CELL_VOLTAGE, __CELL_CAPACITY,
                                                                            __MIN_VOLTAGE, __MAX_VOLTAGE,
                                                                            __MAX_CHARGE_RATE, __MAX_DISCHARGE_RATE,
                                                                            __SELF_DISCHARGE_RATE,
                                                                            __COULOMB_EFFICIENCY)

    __THERMAL_PROPS: ThermalCellProperties = DefaultThermalCellProperties()

    pd.set_option('precision', 9)

    def __init__(self, voltage: float, capacity: float, soh: float, battery_config: BatteryConfig,
                 battery_data_config: BatteryDataConfig):
        super().__init__(voltage, capacity, soh, self.__ELECTRICAL_PROPS, self.__THERMAL_PROPS, self.__CELL_FORMAT,
                         battery_config)

        self.__log: Logger = Logger(type(self).__name__)

        rint_file: str = battery_data_config.sodium_ion_rint_green_rock_file
        ocv_file: str = battery_data_config.sodium_ion_ocv_green_rock_file

        internal_resistance = pd.read_csv(rint_file)  # Ohm
        soc_arr = internal_resistance.iloc[:, self.__SOC_IDX]
        rint_mat_dch = internal_resistance.iloc[:, self.__RINT_Dch_IDX]
        rint_mat_ch = internal_resistance.iloc[:, self.__RINT_Ch_IDX]
        self.__rint_dch_interp1d = scipy.interpolate.interp1d(soc_arr, rint_mat_dch, kind='linear')
        self.__rint_ch_interp1d = scipy.interpolate.interp1d(soc_arr, rint_mat_ch, kind='linear')

        #ocv = pd.read_csv(ocv_file)
        #soc_arr = ocv.iloc[:, self.__SOC_IDX]
        #ocv_mat_ch = ocv.iloc[:, self.__OCV_CH_IDX]
        #ocv_mat_dch = ocv.iloc[:, self.__OCV_IDX]
        #self.__ocv_ch_interp1d = scipy.interpolate.interp1d(soc_arr, ocv_mat_ch, kind='linear')
        #self.__ocv_dch_interp1d = scipy.interpolate.interp1d(soc_arr, ocv_mat_dch, kind='linear')

    def get_open_circuit_voltage(self, battery_state: LithiumIonState) -> float:
        '''Parameters build with ocv fitting'''
        a1 = 4.141
        a2 = -2.883
        a3 = -12.27
        a4 = 21.21
        a5 = -13.75
        a6 = 4.506
        a7 = 0.815

        soc = battery_state.soc

        ocv = a7 + soc*(a6 + a5*soc + a4*soc**2 + a3*soc**3 + a2*soc**4 + a1*soc**5)

        return ocv * self.get_serial_scale()

        #ocv = pd.read_csv(ocv_file)
        #soc_arr = ocv.iloc[:, self.__SOC_IDX]
        #ocv_mat_ch = ocv.iloc[:, self.__OCV_IDX]
        #self.__ocv_ch_interp1d = scipy.interpolate.interp1d(soc_arr, ocv_mat_ch, kind='linear')

    #def get_internal_resistance(self, battery_state: LithiumIonState) -> float:
     #   rint = 0.33784
      #  return float(rint) / self.get_parallel_scale() * self.get_serial_scale()

    def get_internal_resistance(self, battery_state: LithiumIonState) -> float:
        if battery_state.is_charge:
            rint = self.__rint_ch_interp1d(battery_state.soc)
        else:
            rint = self.__rint_dch_interp1d(battery_state.soc)
        return float(rint) / self.get_parallel_scale() * self.get_serial_scale()

    #def get_open_circuit_voltage(self, battery_state: LithiumIonState) -> float:
     #   ocv = self.__ocv_ch_interp1d(battery_state.soc)
      #  return float(ocv) / self.get_parallel_scale() * self.get_serial_scale()

    #def get_open_circuit_voltage(self, battery_state: LithiumIonState) -> float:
     #   if battery_state.is_charge:
      #      ocv = self.__ocv_ch_interp1d(battery_state.soc)
       # else:
        #    ocv = self.__ocv_dch_interp1d(battery_state.soc)
        #return float(ocv) / self.get_parallel_scale() * self.get_serial_scale()

    def close(self) -> None:
        self.__log.close()
