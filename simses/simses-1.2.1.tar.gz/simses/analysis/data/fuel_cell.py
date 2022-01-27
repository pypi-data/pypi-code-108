import pandas

from simses.analysis.data.abstract_data import Data
from simses.commons.state.technology.fuel_cell import FuelCellState
from simses.commons.config.simulation.general import GeneralSimulationConfig


class FuelCellData(Data):
    """
    Provides time series data from FuelCellState
    """

    def __init__(self, config: GeneralSimulationConfig, data: pandas.DataFrame):
        super().__init__(config, data)
        self.__config = config

    @property
    def id(self) -> str:
        return str(int(self._get_first_value(FuelCellState.SYSTEM_AC_ID))) + '.' + \
               str(int(self._get_first_value(FuelCellState.SYSTEM_DC_ID)))

    @property
    def time(self):
        return self._get_data(FuelCellState.TIME)

    @property
    def power(self):
        return self.current * self.voltage

    @property
    def dc_power(self):
        return self.power

    @property
    def energy_difference(self):
        pass

    @property
    def soc(self):
        pass

    @property
    def capacity(self):
        pass

    @property
    def state_of_health(self):
        pass

    @property
    def storage_fulfillment(self):
        return self._get_data(FuelCellState.FULFILLMENT)

    @property
    def current(self):
        return self._get_data(FuelCellState.CURRENT)

    @property
    def voltage(self):
        return self._get_data(FuelCellState.VOLTAGE)

    @property
    def current_density(self):
        return self._get_data(FuelCellState.CURRENT_DENSITY)

    @property
    def hydrogen_use(self):
        return self._get_data(FuelCellState.HYDROGEN_USE)

    @property
    def pressure_anode(self):
        return self._get_data(FuelCellState.PRESSURE_ANODE)

    @property
    def pressure_cathode(self):
        return self._get_data(FuelCellState.PRESSURE_CATHODE)

    @property
    def temperature(self):
        return self._get_data(FuelCellState.TEMPERATURE)

    @classmethod
    def get_system_data(cls, path: str, config: GeneralSimulationConfig) -> list:
        system_data: [pandas.DataFrame] = cls._get_system_data_for(path, FuelCellState, FuelCellState.TIME,
                                                                   FuelCellState.SYSTEM_AC_ID,
                                                                   FuelCellState.SYSTEM_DC_ID)
        res: [FuelCellData] = list()
        for data in system_data:
            res.append(FuelCellData(config, data))
        return res
