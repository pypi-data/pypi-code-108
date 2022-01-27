import pandas

from simses.analysis.data.abstract_data import Data
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.state.energy_management import EnergyManagementState


class EnergyManagementData(Data):
    """
    Provides time series data from EnergyManamgentState
    """

    def __init__(self, config: GeneralSimulationConfig, data: pandas.DataFrame):
        super().__init__(config, data)

    @property
    def id(self) -> str:
        return '0.0'

    @property
    def time(self):
        return self._get_data(EnergyManagementState.TIME)

    @property
    def power(self):
        pass

    @property
    def dc_power(self):
        pass

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
        pass

    @property
    def load_power(self):
        return self._get_data(EnergyManagementState.LOAD_POWER)

    @property
    def pv_power(self):
        return self._get_data(EnergyManagementState.PV_POWER)

    @property
    def fcr_max_power(self):
        return self._get_data(EnergyManagementState.FCR_MAX_POWER)

    @property
    def idm_power(self):
        return self._get_data(EnergyManagementState.IDM_POWER)

    @property
    def peakshaving_limit(self):
        return self._get_data(EnergyManagementState.PEAKSHAVING_LIMIT)

    @classmethod
    def get_system_data(cls, path: str, config: GeneralSimulationConfig) -> list:
        system_data: [pandas.DataFrame] = cls._get_system_data_for(path, EnergyManagementState, EnergyManagementState.TIME)
        res: [EnergyManagementData] = list()
        for data in system_data:
            res.append(EnergyManagementData(config, data))
        return res
