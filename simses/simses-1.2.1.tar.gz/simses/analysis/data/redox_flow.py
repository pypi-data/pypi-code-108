import pandas

from simses.analysis.data.abstract_data import Data
from simses.analysis.utils import get_mean_for
from simses.analysis.utils import get_positive_values_from, get_sum_for, get_negative_values_from
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.state.technology.redox_flow import RedoxFlowState


class RedoxFlowData(Data):
    """
    Provides time series data from RedoxFlowState
    """

    def __init__(self, config: GeneralSimulationConfig, data: pandas.DataFrame):
        super().__init__(config, data)
        self.__config = config

    @property
    def id(self) -> str:
        return str(int(self._get_first_value(RedoxFlowState.SYSTEM_AC_ID))) + '.' + \
               str(int(self._get_first_value(RedoxFlowState.SYSTEM_DC_ID)))

    @property
    def time(self):
        return self._get_data(RedoxFlowState.TIME)

    @property
    def power(self):
        return self._get_data(RedoxFlowState.POWER)

    @property
    def pump_power(self):
        return self._get_data(RedoxFlowState.PUMP_POWER)

    @property
    def dc_power(self):
        return self.power

    @property
    def energy_difference(self):
        soc = self._get_difference(RedoxFlowState.SOC)
        capacity = self.initial_capacity
        return soc * capacity

    @property
    def soc(self):
        return self._get_data(RedoxFlowState.SOC)

    @property
    def soc_stack(self):
        return self._get_data(RedoxFlowState.SOC_STACK)

    @property
    def capacity(self):
        return self._get_data(RedoxFlowState.CAPACITY) / 1000.0

    @property
    def state_of_health(self):
        return self._get_data(RedoxFlowState.SOH)

    @property
    def resistance(self):
        return self._get_data(RedoxFlowState.INTERNAL_RESISTANCE)

    @property
    def temperature(self):
        return self._get_data(RedoxFlowState.TEMPERATURE)

    @property
    def storage_fulfillment(self):
        return self._get_data(RedoxFlowState.FULFILLMENT)

    @classmethod
    def get_system_data(cls, path: str, config: GeneralSimulationConfig) -> list:
        system_data: [pandas.DataFrame] = cls._get_system_data_for(path, RedoxFlowState, RedoxFlowState.TIME,
                                                                   RedoxFlowState.SYSTEM_AC_ID, RedoxFlowState.SYSTEM_DC_ID)
        res: [RedoxFlowData] = list()
        for data in system_data:
            res.append(RedoxFlowData(config, data))
        return res

    @property
    def current(self):
        return self._get_data(RedoxFlowState.CURRENT)

    @property
    def mean_open_circuit_voltage(self):
        ocv = self._get_data(RedoxFlowState.OPEN_CIRCUIT_VOLTAGE)
        return get_mean_for(ocv)

    @property
    def charge_current_sec(self) -> float:
        """
        Charge energy in kWh (as positive values)

        Returns
        -------

        """
        data = get_positive_values_from(self.current)
        return get_sum_for(data) * self.__config.timestep

    @property
    def discharge_current_sec(self) -> float:
        """
        Discharge energy in kWh (as positive values)

        Returns
        -------

        """
        data = -1 * get_negative_values_from(self.current)
        return get_sum_for(data) * self.__config.timestep

    @property
    def charge_difference(self):
        soc_difference = self._get_difference(RedoxFlowState.SOC)
        charge_total = self.initial_capacity * 1000 * 3600 / self.mean_open_circuit_voltage
        return soc_difference * charge_total


