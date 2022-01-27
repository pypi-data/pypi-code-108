import pandas

from simses.analysis.data.abstract_data import Data
from simses.analysis.utils import get_sum_for, get_positive_values_from
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.constants import Hydrogen
from simses.commons.state.technology.electrolyzer import ElectrolyzerState


class ElectrolyzerData(Data):
    """
    Provides time series data from ElectrolyzerState
    """

    def __init__(self, config: GeneralSimulationConfig, data: pandas.DataFrame):
        super().__init__(config, data)
        self.__config = config

    @property
    def id(self) -> str:
        return str(int(self._get_first_value(ElectrolyzerState.SYSTEM_AC_ID))) + '.' + \
               str(int(self._get_first_value(ElectrolyzerState.SYSTEM_DC_ID)))

    @property
    def time(self):
        return self._get_data(ElectrolyzerState.TIME)

    @property
    def power(self):
        return self._get_data(ElectrolyzerState.POWER)

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
        return self._get_data(ElectrolyzerState.FULFILLMENT)

    @property
    def current(self):
        return self._get_data(ElectrolyzerState.CURRENT)

    @property
    def current_density(self):
        return self._get_data(ElectrolyzerState.CURRENT_DENSITY)

    @property
    def hydrogen_outflow(self):
        return self._get_data(ElectrolyzerState.HYDROGEN_OUTFLOW)

    @property
    def hydrogen_production(self):
        return self._get_data(ElectrolyzerState.HYDROGEN_PRODUCTION)

    @property
    def pressure_anode(self):
        return self._get_data(ElectrolyzerState.PRESSURE_ANODE)

    @property
    def pressure_cathode(self):
        return self._get_data(ElectrolyzerState.PRESSURE_CATHODE)

    @property
    def part_pressure_h2(self):
        return self._get_data(ElectrolyzerState.PART_PRESSURE_H2)

    @property
    def part_pressure_o2(self):
        return self._get_data(ElectrolyzerState.PART_PRESSURE_O2)

    @property
    def sat_pressure_h20(self):
        return self._get_data(ElectrolyzerState.SAT_PRESSURE_H2O)

    @property
    def temperature(self):
        return self._get_data(ElectrolyzerState.TEMPERATURE)

    @property
    def convection_heat(self):
        return self._get_data(ElectrolyzerState.CONVECTION_HEAT)

    @property
    def power_gas_drying(self):
        return self._get_data(ElectrolyzerState.POWER_GAS_DRYING)

    @property
    def power_compressor(self):
        return self._get_data(ElectrolyzerState.POWER_COMPRESSOR)

    @property
    def power_pump(self):
        return self._get_data(ElectrolyzerState.POWER_PUMP)

    @property
    def power_water_heating(self):
        return self._get_data(ElectrolyzerState.POWER_WATER_HEATING)

    @property
    def total_h2_production(self):
        return self._get_data(ElectrolyzerState.TOTAL_HYDROGEN_PRODUCTION)

    @property
    def resistance_increase_cyclic(self):
        return self._get_data(ElectrolyzerState.RESISTANCE_INCREASE_CYCLIC)

    @property
    def resistance_increase_calendar(self):
        return self._get_data(ElectrolyzerState.RESISTANCE_INCREASE_CALENDAR)

    @property
    def resistance_increase(self):
        return self._get_data(ElectrolyzerState.RESISTANCE_INCREASE)

    @property
    def exchange_current_dens_decrease_cyclic(self):
        return self._get_data(ElectrolyzerState.EXCHANGE_CURRENT_DENS_DECREASE_CYCLIC)

    @property
    def exchange_current_dens_decrease_calendar(self):
        return self._get_data(ElectrolyzerState.EXCHANGE_CURRENT_DENS_DECREASE_CALENDAR)

    @property
    def exchange_current_dens_decrease(self):
        return self._get_data(ElectrolyzerState.EXCHANGE_CURRENT_DENS_DECREASE)

    @property
    def soh(self):
        return self._get_data(ElectrolyzerState.SOH)

    @property
    def total_energy_pump(self):
        return get_sum_for(self.power_pump) * self.convert_watt_to_kWh

    @property
    def total_energy_compressor(self):
        return get_sum_for(self.power_compressor) * self.convert_watt_to_kWh

    @property
    def total_energy_gas_drying(self):
        return get_sum_for(self.power_gas_drying) * self.convert_watt_to_kWh

    @property
    def total_energy_heating(self):
        return get_sum_for(get_positive_values_from(self.power_water_heating)) * self.convert_watt_to_kWh

    @property
    def total_energy_reaction(self):
        return get_sum_for(self.power) * self.convert_watt_to_kWh

    @property
    def total_energy_h2_lhv(self):
        return get_sum_for(
            self.hydrogen_outflow) * self.__config.timestep * 2 * Hydrogen.MOLAR_MASS_HYDROGEN * Hydrogen.LOWER_HEATING_VALUE

    @property
    def total_amount_h2_kg(self):
        return get_sum_for(self.hydrogen_outflow) * self.__config.timestep * 2 * Hydrogen.MOLAR_MASS_HYDROGEN

    @property
    def total_amount_h2_nqm(self):
        return get_sum_for(self.hydrogen_outflow) * self.__config.timestep * 2 * \
               Hydrogen.MOLAR_MASS_HYDROGEN * Hydrogen.NORM_QUBIC_M

    @classmethod
    def get_system_data(cls, path: str, config: GeneralSimulationConfig) -> list:
        system_data: [pandas.DataFrame] = cls._get_system_data_for(path, ElectrolyzerState, ElectrolyzerState.TIME,
                                                                   ElectrolyzerState.SYSTEM_AC_ID,
                                                                   ElectrolyzerState.SYSTEM_DC_ID)
        res: [ElectrolyzerData] = list()
        for data in system_data:
            res.append(ElectrolyzerData(config, data))
        return res
