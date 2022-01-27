import pandas

from simses.analysis.data.abstract_data import Data
from simses.analysis.utils import get_sum_for, get_positive_values_from
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.constants import Hydrogen
from simses.commons.state.technology.hydrogen import HydrogenState


class HydrogenData(Data):
    """
    DEPRECATED - Provides time series data from HydrogenState
    """

    def __init__(self, config: GeneralSimulationConfig, data: pandas.DataFrame):
        super().__init__(config, data)
        self.__config = config

    @property
    def id(self) -> str:
        return str(int(self._get_first_value(HydrogenState.SYSTEM_AC_ID))) + '.' + \
               str(int(self._get_first_value(HydrogenState.SYSTEM_DC_ID)))

    @property
    def time(self):
        return self._get_data(HydrogenState.TIME)

    @property
    def power(self):
        return self._get_data(HydrogenState.POWER)

    @property
    def dc_power(self):
        return self.power

    @property
    def energy_difference(self):
        soc = self._get_difference(HydrogenState.SOC)
        capacity = self.initial_capacity
        return soc * capacity

    @property
    def soc(self):
        return self._get_data(HydrogenState.SOC)

    @property
    def capacity(self):
        return self._get_data(HydrogenState.CAPACITY) / 1000.0

    @property
    def state_of_health(self):
        return self._get_data(HydrogenState.SOH)

    @property
    def fulfillment(self):
        return self._get_data(HydrogenState.FULFILLMENT)

    @property
    def current_el(self):
        return self._get_data(HydrogenState.CURRENT_EL)

    @property
    def current_density_el(self):
        return self._get_data(HydrogenState.CURRENT_DENSITY_EL)

    @property
    def ref_voltage_el(self):
        return self._get_data(HydrogenState.REFERENCE_VOLTAGE_EL)

    @property
    def hydrogen_outflow(self):
        return self._get_data(HydrogenState.HYDROGEN_OUTFLOW)

    @property
    def hydrogen_production(self):
        return self._get_data(HydrogenState.HYDROGEN_PRODUCTION)

    @property
    def pressure_anode_el(self):
        return self._get_data(HydrogenState.PRESSURE_ANODE_EL)

    @property
    def pressure_cathode_el(self):
        return self._get_data(HydrogenState.PRESSURE_CATHODE_EL)

    @property
    def part_pressure_h2_el(self):
        return self._get_data(HydrogenState.PART_PRESSURE_H2_EL)

    @property
    def part_pressure_o2_el(self):
        return self._get_data(HydrogenState.PART_PRESSURE_O2_EL)

    @property
    def sat_pressure_h20_el(self):
        return  self._get_data(HydrogenState.SAT_PRESSURE_H2O_EL)

    @property
    def tank_pressure(self):
        return self._get_data(HydrogenState.TANK_PRESSURE)

    @property
    def temperature_el(self):
        return self._get_data(HydrogenState.TEMPERATURE_EL)

    @property
    def storage_fulfillment(self):
        return self._get_data(HydrogenState.FULFILLMENT)

    @property
    def convection_heat(self):
        return self._get_data(HydrogenState.CONVECTION_HEAT)

    @property
    def power_water_heating_el(self):
        return self._get_data(HydrogenState.POWER_WATER_HEATING_EL)

    @property
    def power_pump_el(self):
        return self._get_data(HydrogenState.POWER_PUMP_EL)

    @property
    def power_gas_drying(self):
        return self._get_data(HydrogenState.POWER_GAS_DRYING)

    @property
    def power_compressor(self):
        return self._get_data(HydrogenState.POWER_COMPRESSOR)

    @property
    def total_h2_production(self):
        return self._get_data(HydrogenState.TOTAL_HYDROGEN_PRODUCTION)

    @property
    def resistance_increase_cyclic_el(self):
        return self._get_data(HydrogenState.RESISTANCE_INCREASE_CYCLIC_EL)

    @property
    def resistance_increase_calendar_el(self):
        return self._get_data(HydrogenState.RESISTANCE_INCREASE_CALENDAR_EL)

    @property
    def resistance_increase_el(self):
        return self._get_data(HydrogenState.RESISTANCE_INCREASE_EL)

    @property
    def exchange_current_dens_decrease_cyclic_el(self):
        return self._get_data(HydrogenState.EXCHANGE_CURRENT_DENS_DECREASE_CYCLIC_EL)

    @property
    def exchange_current_dens_decrease_calendar_el(self):
        return self._get_data(HydrogenState.EXCHANGE_CURRENT_DENS_DECREASE_CALENDAR_EL)

    @property
    def exchange_current_dens_decrease_el(self):
        return self._get_data(HydrogenState.EXCHANGE_CURRENT_DENS_DECREASE_EL)

    @property
    def soh_el(self):
        return self._get_data(HydrogenState.SOH_EL)

    @property
    def total_energy_pump_el(self):
        return get_sum_for(self.power_pump_el) * self.convert_watt_to_kWh

    @property
    def total_energy_compressor(self):
        return get_sum_for(self.power_compressor) * self.convert_watt_to_kWh

    @property
    def total_energy_gas_drying(self):
        return get_sum_for(self.power_gas_drying) * self.convert_watt_to_kWh

    @property
    def total_energy_heating(self):
        return get_sum_for(get_positive_values_from(self.power_water_heating_el)) * self.convert_watt_to_kWh

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
        system_data: [pandas.DataFrame] = cls._get_system_data_for(path, HydrogenState, HydrogenState.TIME,
                                                                   HydrogenState.SYSTEM_AC_ID,
                                                                   HydrogenState.SYSTEM_DC_ID)
        res: [HydrogenData] = list()
        for data in system_data:
            res.append(HydrogenData(config, data))
        return res


