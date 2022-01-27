import numpy
import scipy.interpolate

from simses.commons.config.data.battery import BatteryDataConfig
from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.commons.utils.cell_reader import IseaCellReader
from simses.technology.lithium_ion.cell.electric.default import DefaultElectricalCellProperties
from simses.technology.lithium_ion.cell.format.round_18650 import RoundCell18650
from simses.technology.lithium_ion.cell.thermal.default import DefaultThermalCellProperties
from simses.technology.lithium_ion.cell.type import CellType


class IseaCellType(CellType):

    # TODO
    # 1) Make cell type only depend on values from cell reader, no hardcoded values anymore
    # -done- 2) How to handle multiple input files? How to instantiate multiple cell types?
    #   a) One distinct cell type for each file --- drawback: very inconvenient for > 100 cell files
    #   b) Instantiate all cell types in one directory --- how to make this configurable?
    # -> c) file name handed over in constructor of cell type --- batch processing sets files, config could be tricky
    # 3) Documentation is missing
    # 4) Tests are missing

    __EXTENSION: str = '.xml'

    def __init__(self, voltage: float, capacity: float, soh: float, battery_config: BatteryConfig,
                 battery_data_config: BatteryDataConfig, file_name: str):
        super().__init__(voltage, capacity, soh, DefaultElectricalCellProperties(), DefaultThermalCellProperties(),
                         RoundCell18650(), battery_config)
        self.__name: str = type(self).__name__ + ' with ' + file_name
        cell: IseaCellReader = IseaCellReader(battery_data_config.isea_cell_dir + file_name + self.__EXTENSION)
        ocv_mat: numpy.ndarray = cell.get_open_cicuit_voltage()
        ocv_soc_arr: numpy.ndarray = cell.get_open_cicuit_voltage_soc()
        ocv_temp_arr: numpy.ndarray = cell.get_open_cicuit_voltage_temperature()
        self.__open_circuit_voltage_interpolation = scipy.interpolate.interp2d(ocv_soc_arr, ocv_temp_arr.T, ocv_mat,
                                                                               kind='linear')
        rint_mat: numpy.ndarray = cell.get_internal_resistance()
        rint_soc_arr: numpy.ndarray = cell.get_internal_resistance_soc()
        rint_temp_arr: numpy.ndarray = cell.get_internal_resistance_temperature()
        self.__internal_resistance_interpolation = scipy.interpolate.interp2d(rint_soc_arr, rint_temp_arr.T, rint_mat,
                                                                              kind='linear')

    def get_open_circuit_voltage(self, battery_state: LithiumIonState) -> float:
        soc: float = battery_state.soc * 100.0
        temp: float = battery_state.temperature - 273.15
        res: float = float(self.__open_circuit_voltage_interpolation(soc, temp))
        # print(soc, temp, res)
        return res * self.get_serial_scale()

    def get_internal_resistance(self, battery_state: LithiumIonState) -> float:
        soc: float = battery_state.soc * 100.0
        temp: float = battery_state.temperature - 273.15
        res: float = float(self.__internal_resistance_interpolation(soc, temp))
        # print(soc, temp, res)
        return res / self.get_parallel_scale() * self.get_serial_scale()

    def get_name(self) -> str:
        return self.__name

    def close(self):
        pass
