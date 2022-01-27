import pandas
from simses.analysis.data.abstract_data import Data
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.state.technology.lithium_ion import LithiumIonState


class LithiumIonData(Data):
    """
    Provides time series data from LithiumIonState
    """

    def __init__(self, config: GeneralSimulationConfig, data: pandas.DataFrame):
        super().__init__(config, data)

    @property
    def id(self) -> str:
        return str(int(self._get_first_value(LithiumIonState.SYSTEM_AC_ID))) + '.' + \
               str(int(self._get_first_value(LithiumIonState.SYSTEM_DC_ID)))

    @property
    def time(self):
        return self._get_data(LithiumIonState.TIME)

    @property
    def power(self):
        return self.voltage * self.current

    @property
    def current(self):
        return self._get_data(LithiumIonState.CURRENT)

    @property
    def voltage(self):
        return self._get_data(LithiumIonState.VOLTAGE)

    @property
    def dc_power(self):
        return self.power

    @property
    def energy_difference(self):
        # initial_soc = self._get_first_value(LithiumIonState.SOC)
        # last_soc = self._get_last_value(LithiumIonState.SOC)
        # initial_capacity = float(self.capacity[0])
        # last_capacity = float(self.capacity[-1])
        # return last_soc * last_capacity - initial_soc * initial_capacity
        initial_soe = float(self.soe[0])
        last_soe = float(self.soe[-1])
        return last_soe - initial_soe

    @property
    def soe(self):
        return self._get_data(LithiumIonState.SOE) / 1000.0

    @property
    def soc(self):
        return self._get_data(LithiumIonState.SOC)

    @property
    def capacity(self):
        return self._get_data(LithiumIonState.CAPACITY) / 1000.0

    @property
    def state_of_health(self):
        return self._get_data(LithiumIonState.SOH)

    @property
    def resistance(self):
        return self._get_data(LithiumIonState.INTERNAL_RESISTANCE)

    @property
    def resistance_increase(self):
        return self._get_data(LithiumIonState.RESISTANCE_INCREASE)

    @property
    def storage_fulfillment(self):
        return self._get_data(LithiumIonState.FULFILLMENT)

    @property
    def temperature(self):
        return self._get_data(LithiumIonState.TEMPERATURE)

    @property
    def capacity_loss_calendar(self):
        return self._get_data(LithiumIonState.CAPACITY_LOSS_CALENDRIC)

    @property
    def capacity_loss_cyclic(self):
        return self._get_data(LithiumIonState.CAPACITY_LOSS_CYCLIC)

    @property
    def resistance_increase_calendar(self):
        return self._get_data(LithiumIonState.RESISTANCE_INCREASE_CALENDRIC)

    @property
    def resistance_increase_cyclic(self):
        return self._get_data(LithiumIonState.RESISTANCE_INCREASE_CYCLIC)

    @classmethod
    def get_system_data(cls, path: str, config: GeneralSimulationConfig) -> list:
        system_data: [pandas.DataFrame] = cls._get_system_data_for(path, LithiumIonState, LithiumIonState.TIME,
                                                                   LithiumIonState.SYSTEM_AC_ID, LithiumIonState.SYSTEM_DC_ID)
        res: [LithiumIonData] = list()
        for data in system_data:
            res.append(LithiumIonData(config, data))
        return res


