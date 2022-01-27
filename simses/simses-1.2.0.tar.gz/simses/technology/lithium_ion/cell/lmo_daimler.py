import pandas as pd
import scipy.interpolate

from simses.commons.config.data.battery import BatteryDataConfig
from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.electric.properties import ElectricalCellProperties
from simses.technology.lithium_ion.cell.format.abstract import CellFormat
from simses.technology.lithium_ion.cell.format.prismatic import PrismaticCell
from simses.technology.lithium_ion.cell.thermal.properties import ThermalCellProperties
from simses.technology.lithium_ion.cell.type import CellType


class DaimlerLMO(CellType):
    """A LMO (Daimler LMO) is a special cell type and inherited by CellType"""
    """ Source: 
        field data from fcr storage system
    """
    __SOC_HEADER = 'SOC'
    __SOC_IDX = 0
    __DOC_IDX = 0
    __OCV_IDX = 1
    __TEMP_IDX = 1
    __C_RATE_IDX = 0
    __ETA_IDX = 1
    __LENGTH_TEMP_ARRAY = 40
    __LENGTH_SOC_ARRAY = 1001
    __LENGTH_DOC_ARRAY = 1001

    __CELL_VOLTAGE = 3.7  # V
    __CELL_CAPACITY = 50.0  # Ah
    __MAX_VOLTAGE: float = 4.095  # V
    __MIN_VOLTAGE: float = 2.9  # V
    __MIN_TEMPERATURE: float = 248.15  # K
    __MAX_TEMPERATURE: float = 323.15  # K
    __MAX_CHARGE_RATE: float = 2.0  # 1/h
    __MAX_DISCHARGE_RATE: float = 2.0  # 1/h
    __SELF_DISCHARGE_RATE: float = 0.0  # X.X%-soc per day, e.g., 0.015 for 1.5% SOC loss per day
    __MASS: float = 1.7  # kg per cell
    __SPECIFIC_HEAT: float = 823  # J/kgK
    __CONVECTION_COEFFICIENT: float = 15  # W/m2K

    __HEIGHT: float = 113.5  # mm
    __WIDTH: float = 43.8  # mm
    __LENGTH: float = 171.0  # mm

    __COULOMB_EFFICIENCY: float = 1.0  # p.u

    __ELECTRICAL_PROPS: ElectricalCellProperties = ElectricalCellProperties(__CELL_VOLTAGE, __CELL_CAPACITY,
                                                                            __MIN_VOLTAGE, __MAX_VOLTAGE,
                                                                            __MAX_CHARGE_RATE, __MAX_DISCHARGE_RATE,
                                                                            __SELF_DISCHARGE_RATE, __COULOMB_EFFICIENCY)
    __THERMAL_PROPS: ThermalCellProperties = ThermalCellProperties(__MIN_TEMPERATURE, __MAX_TEMPERATURE, __MASS,
                                                                   __SPECIFIC_HEAT, __CONVECTION_COEFFICIENT)
    __CELL_FORMAT: CellFormat = PrismaticCell(__HEIGHT, __WIDTH, __LENGTH)

    # Values from nmc_sanyo_ur18650e (source: https://akkuplus.de/Panasonic-UR18650E-37-Volt-2150mAh-Li-Ion-EOL)

    __USE_FIELD_DATA = False  # use measured data from plant for config (false = lab measurements used)
    __USE_MEASUREMENT = False  # use lab measurement (false = datasheet values)

    if __USE_FIELD_DATA:
        __CELL_RESISTANCE: float = 1.0 * 10 ** (-3)  # Ohm, value from field measurement
    else:
        __CELL_RESISTANCE: float = 0.81 * 10 ** (-3)  # Ohm, value from master's thesis: Gnacy

    def __init__(self, voltage: float, capacity: float, soh: float, battery_config: BatteryConfig,
                 battery_data_config: BatteryDataConfig):
        super().__init__(voltage, capacity, soh, self.__ELECTRICAL_PROPS, self.__THERMAL_PROPS, self.__CELL_FORMAT,
                         battery_config)
        self.__log: Logger = Logger(type(self).__name__)
        rint_file: str = battery_data_config.nmc_molicel_rint_file
        internal_resistance = pd.read_csv(rint_file)  # Ohm
        soc_arr = internal_resistance.iloc[:, self.__SOC_IDX]
        temp_arr = internal_resistance.iloc[:4, self.__TEMP_IDX]
        rint_mat_ch = internal_resistance.iloc[:, 2]
        rint_mat_dch = internal_resistance.iloc[:, 5]
        self.__rint_ch_interp1d = scipy.interpolate.interp1d(soc_arr, rint_mat_ch, kind='linear')
        self.__rint_dch_interp1d = scipy.interpolate.interp1d(soc_arr, rint_mat_dch, kind='linear')
        # TODO these stress factors need to be transferred to the corresponding degradation model
        # capacity_cal_file: str = battery_data_config.nmc_molicel_capacity_cal_file
        # ri_cal_file: str = battery_data_config.nmc_molicel_ri_cal_file
        # capacity_cyc_file: str = battery_data_config.nmc_molicel_capacity_cyc_file
        # ri_cyc_file: str = battery_data_config.nmc_molicel_ri_cyc_file
        # capacity_cyc = pd.read_csv(capacity_cyc_file)  # -
        # capacity_cyc_mat = capacity_cyc.iloc[:self.__LENGTH_DOC_ARRAY, 1]
        # doc_arr = capacity_cyc.iloc[:, self.__DOC_IDX]
        # self.__capacity_cyc_interp1d = scipy.interpolate.interp1d(doc_arr, capacity_cyc_mat, kind='linear')
        # ri_cyc = pd.read_csv(ri_cyc_file)  # -
        # ri_cyc_mat = ri_cyc.iloc[:(self.__LENGTH_DOC_ARRAY + 1), 1]
        # doc_arr = ri_cyc.iloc[:, self.__DOC_IDX]
        # self.__ri_cyc_interp1d = scipy.interpolate.interp1d(doc_arr, ri_cyc_mat, kind='linear')
        # capacity_cal = pd.read_csv(capacity_cal_file)  # -
        # capacity_cal_mat = capacity_cal.iloc[:(self.__LENGTH_TEMP_ARRAY + 1), 2:]
        # soc_arr = capacity_cal.iloc[:, self.__SOC_IDX]
        # temp_arr = capacity_cal.iloc[:(self.__LENGTH_TEMP_ARRAY + 1), self.__TEMP_IDX]
        # self.__capacity_cal_interp1d = scipy.interpolate.interp2d(soc_arr, temp_arr.T, capacity_cal_mat, kind='linear')
        # ri_cal = pd.read_csv(ri_cal_file)  # -
        # ri_cal_mat = ri_cal.iloc[:(self.__LENGTH_TEMP_ARRAY + 1), 2:]
        # soc_arr = ri_cal.iloc[:, self.__SOC_IDX]
        # temp_arr = ri_cal.iloc[:(self.__LENGTH_TEMP_ARRAY + 1), self.__TEMP_IDX]
        # self.__ri_cal_interp1d = scipy.interpolate.interp2d(soc_arr, temp_arr.T, ri_cal_mat, kind='linear')

    def get_open_circuit_voltage(self, battery_state: LithiumIonState) -> float:
        soc: float = battery_state.soc * 100.0
        # Linear OCV fit parameters (field data)
        m = 0.43619
        t = 3.67680

        if self.__USE_MEASUREMENT:  # OCV from measurement MA Gnacy, poly9 fit
            p1 = 7.184106990621546e-16
            p2 = -3.740729945156438e-13
            p3 = 8.302607895987187e-11
            p4 = -1.023080886243304e-08
            p5 = 7.638961638126957e-07
            p6 = -3.543204493824138e-05
            p7 = 0.001009824415000
            p8 = -0.017049050946914
            p9 = 0.165789661369883
            p10 = 2.936578769598463
        else:  # OCV from datasheet, poly9 fit
            p1 = 1.053978763548226e-15
            p2 = -5.472087523147638e-13
            p3 = 1.210062584849170e-10
            p4 = -1.481210133229709e-08
            p5 = 1.091568155357329e-06
            p6 = -4.935612738181030e-05
            p7 = 0.001340177529868
            p8 = -0.020709247233047
            p9 = 0.176208491407495
            p10 = 2.9

        if self.__USE_FIELD_DATA:
            soc = soc / 100
            ocv = m * soc + t
        else:
            ocv = p10 + p9 * soc + p8 * soc ** 2 + p7 * soc ** 3 + p6 * soc ** 4 + p5 * soc ** 5 + \
                    p4 * soc ** 6 + p3 * soc ** 7 + p2 * soc ** 8 + p1 * soc ** 9
        return ocv * self.get_serial_scale()

    def get_internal_resistance(self, battery_state: LithiumIonState) -> float:
        return self.__CELL_RESISTANCE / self.get_parallel_scale() * self.get_serial_scale()

    # TODO these stress factors need to be transferred to the corresponding degradation model
    # def get_stressfkt_ca_cal(self, battery_state: LithiumIonState) -> float:
    #     """
    #     get the stress factor for calendar aging capacity loss
    #
    #     Parameters
    #     ----------
    #     battery_state :
    #
    #     Returns
    #     -------
    #
    #     """
    #     return float(self.__capacity_cal_interp1d(battery_state.soc, battery_state.temperature))
    #
    # def get_stressfkt_ri_cal(self, battery_state: LithiumIonState) -> float:
    #     """
    #     get the stress factor for calendar aging capacity loss
    #
    #     Parameters
    #     ----------
    #     battery_state :
    #
    #     Returns
    #     -------
    #
    #     """
    #     return float(self.__ri_cal_interp1d(battery_state.soc, battery_state.temperature))
    #
    # def get_stressfkt_ca_cyc(self, doc: float) -> float:
    #     return float(self.__capacity_cyc_interp1d(doc))
    #
    # def get_stressfkt_ri_cyc(self, doc: float) -> float:
    #     return float(self.__ri_cyc_interp1d(doc))

    def close(self):
        self.__log.close()
