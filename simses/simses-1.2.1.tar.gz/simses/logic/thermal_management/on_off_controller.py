from simses.logic.thermal_management.thermal_management import ThermalManagement
from simses.system.auxiliary.heating_ventilation_air_conditioning.fan import Fan
from simses.system.thermal.model.zero_d_system_thermal_model import ZeroDSystemThermalModel
from numpy import sign
import pandas as pd
import os
import time


class OnOffController(ThermalManagement):

    TEMPERATURE_DEAD_BAND: float = 2.0  # in K

    def __init__(self, set_point: float, hvac_max_thermal_power: float):
        super().__init__()
        self.__set_temperature = set_point  # K
        self.__hvac_rated_thermal_power = hvac_max_thermal_power  # W
        self.__export = False

        # Export running data
        if self.__export:
            self.__file_name = os.getcwd() + '\\controller_running_data\\Results' + str(time.time()) + '.csv'
            df = pd.DataFrame(['Ti', 'Ta', 'Total Thermal Power', 'HVAC Thermal Power', 'Required thermal power', 'HVAC Limit']).T
            df.to_csv(self.__file_name, header=None, index=None)

    def compute(self, internal_air_temperature: float, ambient_air_temperature: float, air_mass: float,
                air_density: float, time_step: float, fan: Fan) -> list:

        if abs(internal_air_temperature - self.__set_temperature) > self.TEMPERATURE_DEAD_BAND:
            required_thermal_power = ZeroDSystemThermalModel.AIR_SPECIFIC_HEAT * (internal_air_temperature - self.__set_temperature) * air_mass / time_step  # W
            rated_supply_temperature = float(self.__set_temperature - sign(required_thermal_power) * 10)  # K
            rated_fresh_air_thermal_power = fan.rated_airflow * air_density * (internal_air_temperature - ambient_air_temperature) * ZeroDSystemThermalModel.AIR_SPECIFIC_HEAT  # W
            max_physical_fresh_air_thermal_power = air_mass * (internal_air_temperature - ambient_air_temperature) * ZeroDSystemThermalModel.AIR_SPECIFIC_HEAT / time_step  # W

            if sign(required_thermal_power) == sign(rated_fresh_air_thermal_power):
                # if the fresh air thermal power is usable
                fresh_air_thermal_power = float(min(abs(rated_fresh_air_thermal_power), abs(max_physical_fresh_air_thermal_power)) * sign(rated_fresh_air_thermal_power))
                if (fresh_air_thermal_power / required_thermal_power) >= 0.999 or (ambient_air_temperature - self.__set_temperature) / (rated_supply_temperature - self.__set_temperature) >= 0.999:
                    # first case: fresh air thermal power is enough
                    # or fresh air and HVAC cannot be working at the same time, and fresh air thermal power is larger
                    # example: set point 298.15K, HVAC supply 288.15K, ambient 280K
                    hvac_thermal_power = 0.0  # W
                else:
                    # second case: the rest of demand from HVAC
                    hvac_thermal_power = float(min(abs(self.__hvac_rated_thermal_power), abs(ZeroDSystemThermalModel.AIR_SPECIFIC_HEAT * (ambient_air_temperature - rated_supply_temperature) * fan.rated_airflow * air_density)) * sign(required_thermal_power))  # W
            else:
                # if the fresh air thermal power cannot be used
                # third case: HVAC only
                fresh_air_thermal_power = 0.0
                hvac_thermal_power = float(min(abs(self.__hvac_rated_thermal_power), abs(ZeroDSystemThermalModel.AIR_SPECIFIC_HEAT * (internal_air_temperature - rated_supply_temperature) * fan.rated_airflow * air_density)) * sign(required_thermal_power))  # W

            total_thermal_power = float(hvac_thermal_power + fresh_air_thermal_power)  # W
            fan.run(fan.rated_airflow)

            # Export running data
            if self.__export:
                data_list = [float(internal_air_temperature), ambient_air_temperature, total_thermal_power,
                         hvac_thermal_power, required_thermal_power,
                         self.__hvac_rated_thermal_power]
                df = pd.DataFrame(data_list).T
                df.to_csv(self.__file_name, mode='a', header=None, index=None)

            return [total_thermal_power, hvac_thermal_power]
        else:
            fan.run(0)
            return [0.0, 0.0]
