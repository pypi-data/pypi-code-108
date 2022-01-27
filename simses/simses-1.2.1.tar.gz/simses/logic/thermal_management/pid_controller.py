from simses.logic.thermal_management.thermal_management import ThermalManagement
from simses.system.auxiliary.heating_ventilation_air_conditioning.fan import Fan
from simses.system.thermal.model.zero_d_system_thermal_model import ZeroDSystemThermalModel
from numpy import sign
import pandas as pd
import os
import time


class PIDController(ThermalManagement):

    TEMPERATURE_DEAD_BAND: float = 2.0  # K

    def __init__(self, set_point: float, hvac_max_thermal_power: float):
        super().__init__()
        self.__set_temperature = set_point  # K
        self.__hvac_rated_thermal_power = hvac_max_thermal_power  # W
        self.__kp_coefficient = 10000
        self.__ki_coefficient = 100
        self.__kd_coefficient = 1800
        self.__thermal_power_scaling_factor = 1
        self.__temperature_difference_memory = [0]
        self.__i_temperature_difference = 0


        # Export running data
        # self.__file_name = os.getcwd() + '\\controller_running_data\\Results' + str(time.time()) + '.csv'
        # df = pd.DataFrame(['Ti', 'Ta', 'Total Thermal Power', 'HVAC Thermal Power', 'Fan Power', 'Required thermal power', 'P_Difference', 'I_Difference', 'D_Difference', 'HVAC Limit']).T
        # df.to_csv(self.__file_name, header=None, index=None)

    def compute(self, internal_air_temperature: float, ambient_air_temperature: float, air_mass: float,
                air_density: float, time_step: float, fan: Fan) -> list:
        p_temperature_difference = float(internal_air_temperature - self.__set_temperature)
        self.__i_temperature_difference += p_temperature_difference
        self.__temperature_difference_memory.append(p_temperature_difference)
        d_temperature_difference = (self.__temperature_difference_memory[-1] - self.__temperature_difference_memory[-2])

        required_thermal_power = self.__thermal_power_scaling_factor * \
                                 (self.__kp_coefficient * p_temperature_difference +
                                  self.__ki_coefficient * self.__i_temperature_difference +
                                  self.__kd_coefficient * d_temperature_difference)

        if sign(required_thermal_power) == sign(p_temperature_difference) and abs(p_temperature_difference) > self.TEMPERATURE_DEAD_BAND:  # Filter with deadband to prevent overcooling / overheating

            rated_supply_temperature = float(self.__set_temperature - sign(required_thermal_power) * 10)  # K
            rated_fresh_air_thermal_power = fan.rated_airflow * air_density * (internal_air_temperature - ambient_air_temperature) * ZeroDSystemThermalModel.AIR_SPECIFIC_HEAT  # W
            max_physical_fresh_air_thermal_power = air_mass * (internal_air_temperature - ambient_air_temperature) * ZeroDSystemThermalModel.AIR_SPECIFIC_HEAT / time_step  # W

            if sign(required_thermal_power) == sign(max_physical_fresh_air_thermal_power):
                # if the fresh air thermal power is usable
                fresh_air_thermal_power = min(max(abs(max_physical_fresh_air_thermal_power), abs(rated_fresh_air_thermal_power)), abs(required_thermal_power)) * float(sign(required_thermal_power))  # W
                hvac_thermal_power_limit = fan.rated_airflow * air_density * (ambient_air_temperature - rated_supply_temperature) * ZeroDSystemThermalModel.AIR_SPECIFIC_HEAT  # W
                if fresh_air_thermal_power / required_thermal_power >= 0.999:
                    # first case: the requirement can be met only with fresh air
                    hvac_thermal_power = 0.0  # W
                    airflow = fan.rated_airflow * (fresh_air_thermal_power / rated_fresh_air_thermal_power)  # m3/s
                else:
                    # second case: fresh air thermal power is not enough, the rest is from HVAC
                    hvac_thermal_power = float(min(abs(self.__hvac_rated_thermal_power),
                                                    abs(required_thermal_power - fresh_air_thermal_power),
                                                    abs(hvac_thermal_power_limit)) * sign(required_thermal_power))  # W
                    airflow = fan.rated_airflow  # m3/s
            else:
                # third case: fresh air cannot be used. HVAC only
                fresh_air_thermal_power = 0.0  # W
                hvac_thermal_power_limit = fan.rated_airflow * air_density * (internal_air_temperature - rated_supply_temperature) * ZeroDSystemThermalModel.AIR_SPECIFIC_HEAT  # W
                hvac_thermal_power = float(min(abs(self.__hvac_rated_thermal_power), abs(required_thermal_power - fresh_air_thermal_power), abs(hvac_thermal_power_limit)) * sign(required_thermal_power))  # W
                if internal_air_temperature != rated_supply_temperature:
                    airflow = hvac_thermal_power / ((internal_air_temperature - rated_supply_temperature) * ZeroDSystemThermalModel.AIR_SPECIFIC_HEAT * air_density)  # m3/s
                else:
                    airflow = 0.0  # m3/s
        else:
            hvac_thermal_power = 0.0  # W
            fresh_air_thermal_power = 0.0  # W
            airflow = 0.0  # m3/s
        total_thermal_power = float(hvac_thermal_power + fresh_air_thermal_power)  # W
        fan.run(airflow)

        # Export running data
        # data_list = [float(internal_air_temperature), ambient_air_temperature, total_thermal_power, hvac_thermal_power,
        #             fan.electricity_consumption, required_thermal_power, p_temperature_difference,
        #             self.__i_temperature_difference, d_temperature_difference, self.__hvac_rated_thermal_power]
        # df = pd.DataFrame(data_list).T
        # df.to_csv(self.__file_name, mode='a', header=None, index=None)
        return [float(total_thermal_power), float(hvac_thermal_power)]

