from numpy import sign
from simses.commons.config.simulation.system import StorageSystemConfig
from simses.logic.thermal_management.on_off_controller import OnOffController
from simses.logic.thermal_management.pid_controller import PIDController
from simses.system.auxiliary.heating_ventilation_air_conditioning.hvac import HeatingVentilationAirConditioning
from simses.system.auxiliary.heating_ventilation_air_conditioning.fan import Fan


class FixCOPHeatingVentilationAirConditioning(HeatingVentilationAirConditioning):

    def __init__(self, hvac_configuration: list):
        super().__init__()

        # Get optional user-defined values required for this class
        try:
            self.__max_thermal_power: float = float(hvac_configuration[StorageSystemConfig.HVAC_POWER])
        except IndexError:
            raise Exception('Please specify thermal power for HVAC class' + self.__name__)
        self.__min_thermal_power: float = self.__max_thermal_power * 0.0  # W
        try:
            self.__set_point_temperature = float(hvac_configuration[StorageSystemConfig.HVAC_TEMPERATURE_SETPOINT]) + 273.15  # K
        except (IndexError, ValueError):
            self.__set_point_temperature = 298.15  # K, default value 25 °C
        # source for scop and seer :
        # https://data.toshiba-klima.at/de/Multisplit%20R32%20-%2010,00%20kW%20-%20R32%20-%20Home%20RAS-5M34U2AVG-E%20de.pdf
        # seasonal coefficient of performance (for cooling)
        self.__scop: float = 4.08
        # seasonal energy efficiency ratio (for heating)
        self.__seer: float = 6.31

        # Initialize variables
        self.__electric_power: float = 0  # W
        self.__thermal_power: float = 0  # W
        self.__air_mass: float = 0  # kg
        self.__air_specific_heat: float = 0  # J/kgK
        self.__supply_air_temperature = 288.15  # K

        # Create the Fan
        self.__fan = Fan()

        # Create Thermal Management
        # self.__thermal_management = OnOffController(self.__set_point_temperature, self.__max_thermal_power)
        self.__thermal_management = PIDController(self.__set_point_temperature, self.__max_thermal_power)

    def run_air_conditioning(self, temperature_time_series: [float], temperature_timestep: float, ambient_air_temperature: float) -> None:
        # This HVAC model monitors the air temperature (with respect to the provided set-point)
        # This logic reduces chatter and rapid switching between heating and cooling to some extent
        self.__thermal_power = 0  # W
        self.__electric_power = 0  # W

        total_thermal_power, hvac_thermal_power = self.__thermal_management.compute(temperature_time_series[0], ambient_air_temperature, self.__air_mass, self.__air_density, temperature_timestep, self.__fan)
        self.__thermal_power = float(total_thermal_power)  # W
        hvac_thermal_power = float(hvac_thermal_power)

        # thermal_power is +ve when cooling and -ve when heating
        if abs(total_thermal_power) > 0 and hvac_thermal_power == 0:
            self.__electric_power = self.__fan.electricity_consumption  # W
        elif hvac_thermal_power < 0:
            self.__electric_power = abs(hvac_thermal_power / self.__seer) + self.__fan.electricity_consumption  # W
        elif hvac_thermal_power > 0:
            self.__electric_power = abs(hvac_thermal_power / self.__scop) + self.__fan.electricity_consumption  # W
        else:
            self.__electric_power = 0.0  # W

    def get_max_thermal_power(self) -> float:
        return self.__max_thermal_power

    def get_thermal_power(self) -> float:
        return self.__thermal_power

    def get_electric_power(self) -> float:
        return self.__electric_power

    def get_set_point_temperature(self) -> float:
        return self.__set_point_temperature

    def get_scop(self) -> float:
        return self.__scop

    def get_seer(self) -> float:
        return self.__seer

    def get_temperature_dead_band(self) -> float:
        return self.__thermal_management.TEMPERATURE_DEAD_BAND

    def update_air_parameters(self, air_mass: float = None, air_specific_heat: float = None, air_density: float = None) -> None:
        self.__air_mass = air_mass
        self.__air_specific_heat = air_specific_heat
        self.__air_density = air_density

    def set_electric_power(self, electric_power: float) -> None:
        """Used in cases where multiple runs of the HVAC take place within a SimSES timestep"""
        self.__electric_power = electric_power
