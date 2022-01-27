from numpy import sign
from simses.commons.config.simulation.system import StorageSystemConfig
from simses.system.auxiliary.heating_ventilation_air_conditioning.hvac import HeatingVentilationAirConditioning


class FixCOPHeatingVentilationAirConditioningPIDControl(HeatingVentilationAirConditioning):

    def __init__(self, hvac_configuration: list):
        super().__init__()
        # ---------- HVAC specific parameters ----------
        # source for scop and seer :
        # https://data.toshiba-klima.at/de/Multisplit%20R32%20-%2010,00%20kW%20-%20R32%20-%20Home%20RAS-5M34U2AVG-E%20de.pdf
        self.__scop: float = 4.08  # seasonal coefficient of performance (for cooling)
        self.__seer: float = 6.31  # seasonal energy efficiency ratio (for heating)

        # ---------- input values for thermal_power calculation and control ----------
        # It is possible to give optional parameters and settings for the HVAC in the simulation config-HVAC section.
        # try to get coefficients, if none were given local ones are taken

        # Get optional user-defined values required for this class
        try:
            self.__max_thermal_power: float = float(hvac_configuration[StorageSystemConfig.HVAC_POWER])
        except IndexError:
            raise Exception('Please specify thermal power for HVAC class' + self.__name__)

        self.__min_thermal_power = self.__max_thermal_power * 0
        try:
            self.__battery_temperature_target = float(hvac_configuration[StorageSystemConfig.HVAC_TEMPERATURE_SETPOINT]) + 273.15
        except (IndexError, ValueError):
            self.__battery_temperature_target = 298.15  # default value 25 °C
        try:
            self.__kp_coefficient = float(hvac_configuration[StorageSystemConfig.HVAC_KP_COEFFICIENT])
        except (IndexError, ValueError):
            self.__kp_coefficient = 600
        try:
            self.__ki_coefficient = float(hvac_configuration[StorageSystemConfig.HVAC_KI_COEFFICIENT])
        except (IndexError, ValueError):
            self.__ki_coefficient = 5
        try:
            self.__kd_coefficient = float(hvac_configuration[StorageSystemConfig.HVAC_KD_COEFFICIENT])
        except (IndexError, ValueError):
            self.__kd_coefficient = 1

        # upper boundary for the integral part
        self.__i_temperature_difference_upper_boundary = 1000000

        # TODO Logic for scaling factor
        # self.__max_power_battery = int(self.__system_config.storage_systems_ac[0][1])
        # self.__thermal_power_scaling_factor = (self.__max_power_battery / 100000) * \
        #                                         (self.__energy_capacity_battery / self.__max_power_battery) * 2
        self.__thermal_power_scaling_factor = 27.400000000000002

        # ---------- initializing variables and arrays ----------

        self.__temperature_difference_storage = [0]
        self.__zero_line_for_temperature_difference_plot = [0]
        self.__target_line_for_temperature_plot = [self.__battery_temperature_target]
        self.__thermal_power_storage = [0]
        self.__zero_line_for_thermal_power_plot = [0]
        self.__i_temperature_difference = 0

        self.__electric_power: float = 0
        self.__thermal_power: float = 0

    def run_air_conditioning(self, temperature_time_series: [float], temperature_timestep: float, ambient_air_temperature: float) -> None:
        temperature_steps_for_integration = []
        temperature_time_series = temperature_time_series[1]  # To control the temperature of the first StorageTechnology
        # temperature_difference_storage equals the difference between the actual and the targeted battery temperature
        # zero_line_for_temperature_difference_plot and target_line_for_temperature_plot are just for plotting
        for i in temperature_time_series:
            self.__temperature_difference_storage.append(i - self.__battery_temperature_target)
            self.__zero_line_for_temperature_difference_plot.append(0)
            self.__target_line_for_temperature_plot.append(self.__battery_temperature_target)
            temperature_steps_for_integration.append(i - self.__battery_temperature_target)

        p_temperature_difference = self.__temperature_difference_storage[-1]
        # i_temperature_difference gets calculated by simple "rectangle integration"
        for x in temperature_steps_for_integration:
            self.__i_temperature_difference += x * temperature_timestep

        # setting an upper boundary for the integral part
        if abs(self.__i_temperature_difference) > self.__i_temperature_difference_upper_boundary:
            self.__i_temperature_difference = self.__i_temperature_difference_upper_boundary * \
                                              sign(self.__i_temperature_difference)

        # there were Problems when self.__calculation_time_step equals self.__temperature_timestep because
        #  len(self.__temperature_difference_storage) = 1 in the first cycle
        if len(self.__temperature_difference_storage) == 1:
            d_temperature_difference = self.__temperature_difference_storage[-1]
        else:
            d_temperature_difference = self.__temperature_difference_storage[-1] - \
                                       self.__temperature_difference_storage[-2]
        # thermal_power is +ve when cooling and -ve when heating
        # TODO scale cooling power and boundaries
        thermal_power_required = self.__thermal_power_scaling_factor * \
                                 (self.__kp_coefficient * p_temperature_difference +
                                  self.__ki_coefficient * self.__i_temperature_difference +
                                  self.__kd_coefficient * d_temperature_difference)

        # ---------- running HVAC ----------

        if abs(thermal_power_required) < self.__min_thermal_power:
            self.__thermal_power = 0.0
        elif abs(thermal_power_required) > self.__max_thermal_power:
            self.__thermal_power = self.__max_thermal_power * sign(thermal_power_required)
        else:
            self.__thermal_power = thermal_power_required

        if thermal_power_required > 0:
            self.__electric_power = abs(self.__thermal_power / self.__seer)
        else:
            self.__electric_power = abs(self.__thermal_power / self.__scop)

        self.__thermal_power_storage.append(self.__thermal_power)
        self.__zero_line_for_thermal_power_plot.append(0)

    def get_max_thermal_power(self) -> float:
        return self.__max_thermal_power

    def get_thermal_power(self) -> float:
        return self.__thermal_power

    def get_electric_power(self) -> float:
        return self.__electric_power

    def get_set_point_temperature(self) -> float:
        return self.__battery_temperature_target

    def get_scop(self) -> float:
        return self.__scop

    def get_seer(self) -> float:
        return self.__seer

    def get_temperature_dead_band(self) -> float:
        return self.__thermal_management.TEMPERATURE_DEAD_BAND

    def get_coefficients(self) -> [float, float, float]:
        return [self.__kp_coefficient, self.__ki_coefficient, self.__kd_coefficient]

    def get_plotting_arrays(self) -> [[float], [float], [float], [float], [float], [float]]:
        return [self.__temperature_difference_storage, self.__target_line_for_temperature_plot,
                self.__zero_line_for_temperature_difference_plot, self.__thermal_power_storage,
                self.__zero_line_for_thermal_power_plot]

    def update_air_parameters(self, air_mass: float = None, air_specific_heat: float = None, air_density: float = None) -> None:
        pass

    def set_electric_power(self, electric_power: float) -> None:
        """Used in cases where multiple runs of the HVAC take place within a SimSES timestep"""
        self.__electric_power = electric_power
