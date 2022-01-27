import numpy as np
from scipy.integrate import solve_ivp

from simses.commons.log import Logger
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.state.system import SystemState
from simses.system.auxiliary.auxiliary import Auxiliary
from simses.system.auxiliary.heating_ventilation_air_conditioning.hvac import HeatingVentilationAirConditioning
from simses.system.housing.abstract_housing import Housing
from simses.system.housing.twenty_ft_container import TwentyFtContainer
from simses.system.power_electronics.acdc_converter.abstract_acdc_converter import AcDcConverter
from simses.system.power_electronics.dcdc_converter.abstract_dcdc_converter import DcDcConverter
from simses.system.storage_system_dc import StorageSystemDC
from simses.system.thermal.ambient.ambient_thermal_model import AmbientThermalModel
from simses.system.thermal.model.system_thermal_model import SystemThermalModel
from simses.technology.storage import StorageTechnology


class ZeroDSystemThermalModelSingleStep(SystemThermalModel):
    """This model functions at StorageSystemAC Level.
    """

    def __init__(self, ambient_thermal_model: AmbientThermalModel, housing: Housing,
                 hvac: HeatingVentilationAirConditioning, general_config: GeneralSimulationConfig, dc_systems: [StorageSystemDC], acdc_converter: AcDcConverter):

        # General parameters and config
        super().__init__()
        self.__log: Logger = Logger(type(self).__name__)
        self.start_time: float = general_config.start
        self.sample_time: float = general_config.timestep

        # Storage system parameters
        self.__acdc_converter = acdc_converter
        self.__dc_systems: StorageSystemDC = dc_systems[0]
        self.__dc_dc_converter: DcDcConverter = self.__dc_systems.get_dc_dc_converter()
        self.__storage_technology: StorageTechnology = self.__dc_systems.get_storage_technology()

        # Ambient temperature model
        self.__ambient_thermal_model: AmbientThermalModel = ambient_thermal_model


        # Solar irradiation model
        # Site under construction
        # this is the internal air temperature within the container. Initialized with ambient temperature

        # Housing Model
        self.__housing: TwentyFtContainer = housing  # Link housing object

        # HVAC model
        self.__heating_cooling: HeatingVentilationAirConditioning = hvac
        self.__cooling_power = 0  # in W, -ve implies heating and vice versa
        self.__set_point_temperature: float = self.__heating_cooling.get_set_point_temperature()  # K

        # Initialize simulation parameters
        self.__battery_temperature = self.__dc_systems.state.temperature
        self.__system_air_temperature: float = self.__ambient_thermal_model.get_initial_temperature()  # K internal air temperature

        # Air parameters
        self.__individual_gas_constant = self.universal_gas_constant / self.molecular_weight_air  # J/kgK
        self.__air_density = self.air_pressure / (self.__individual_gas_constant * self.__system_air_temperature)  # kg/m3
        self.update_air_parameters()
        self.__air_specific_heat = 1006  # J/kgK, cp (at constant pressure)
        # Model with p & V constant, i.e. if T rises, mass must decrease.
        # Quantities with reference to ideal gas equation

        # Initialize battery physical parameters
        self.__surface_area_battery = self.__storage_technology.surface_area  # in m2
        self.__mass_battery = self.__storage_technology.mass  # in kg
        self.__specific_heat_capacity_battery = self.__storage_technology.specific_heat  # in J/kgK
        self.__convection_coefficient_cell_air = self.__storage_technology.convection_coefficient  # in W/m2K

        # Site under construction
        # mass of DC/DC converter
        # surface area of DC/DC converter
        # convection coefficient
        # specific heat of DC/DC converter

        # Site under construction
        # mass of AC/DC converter
        # surface area of AC/DC converter
        # convection coefficient
        # specific heat of AC/DC converter

    def update_air_parameters(self):
        self.__air_volume = self.__housing.internal_air_volume  # in m3
        self.__air_mass = self.__air_volume * self.__air_density  # kg

    def calculate_temperature(self, time, state: SystemState, states: [SystemState]) -> None:

        # Update ambient thermal parameters
        ambient_air_temperature = self.__ambient_thermal_model.get_temperature(time)
        radiation_power = 0  # Site under construction
        # radiation_power_per_unit_area = self.__solar_radiation_model.get_irradiance(time)  # for the non-shaded
        # area in W - link this to a radiation model radiation_power = radiation_power_per_unit_area * area  # in W

        # Calculate thermal resistance to heat flow through the walls
        net_thermal_resistance = self.__housing.thickness_L1 / (
                    self.__housing.thermal_conductivity_L1 * self.__housing.internal_surface_area) + \
                                 self.__housing.thickness_L2 / (
                                             self.__housing.thermal_conductivity_L2 * self.__housing.mean_surface_area) + \
                                 self.__housing.thickness_L3 / (
                                             self.__housing.thermal_conductivity_L3 * self.__housing.external_surface_area_total)


        # dc_system_state: SystemState = dc_system_states[0]
        self.__battery_temperature = self.__storage_technology.state.temperature  # in K
        self.__system_air_temperature = state.temperature  # in K
        power_electronics_loss = state.pe_losses + state.dc_power_loss  # in W


        def equation_rhs(t, variable_array):
            # variable_array = [battery_temperature, system_air_temperature, L1_temperature, L3_temperature]
            # Temperature variables: battery_temperature, system_air_temperature, L1_temperature, L3_temperature
            # independent variable: time

            # This logic reduces chatter and rapid switching between heating and cooling to some extent
            if abs(self.__set_point_temperature - variable_array[1]) > 1:
                cooling_power = -self.__air_mass * self.__air_specific_heat * \
                                (self.__set_point_temperature - variable_array[1])  # in W, rough cooling power estimate
                self.__heating_cooling.run_air_conditioning(cooling_power)  # in W, get actual cooling power
                air_conditioning_thermal_power_actual = self.__heating_cooling.get_thermal_power()  # W
                self.__cooling_power = air_conditioning_thermal_power_actual
            else:
                self.__cooling_power = 0

            # Differential equation for change in battery temperature
            d_by_dt_battery_temperature = (state.storage_power_loss -
                                           self.__convection_coefficient_cell_air * self.__surface_area_battery *
                                           (variable_array[0] - variable_array[1])) / \
                                          (self.__mass_battery * self.__specific_heat_capacity_battery)
            # Differential equation for change in system air temperature
            d_by_dt_system_air_temperature = (self.__convection_coefficient_cell_air * self.__surface_area_battery *
                                              (variable_array[0] - variable_array[1]) - self.__cooling_power + power_electronics_loss -
                                              self.__housing.convection_coefficient_air_L1 * self.__housing.internal_surface_area *
                                              (variable_array[1] - variable_array[2])) / (
                                                         self.__air_mass * self.__air_specific_heat)
            # Differential equation for change in L1 temperature
            d_by_dt_L1_temperature = (self.__housing.convection_coefficient_air_L1 * self.__housing.internal_surface_area *
                                                 (variable_array[1] - variable_array[2]) - (variable_array[2]-variable_array[3])/net_thermal_resistance) / \
                                     (self.__housing.mass_L1 * self.__housing.specific_heat_L1)
            # Differential equation for change in L3 temperature
            d_by_dt_L3_temperature = (self.__housing.convection_coefficient_L3_air * self.__housing.external_surface_area_total *
                                      (ambient_air_temperature - variable_array[3]) + radiation_power + (variable_array[2]-variable_array[3]) / net_thermal_resistance) / \
                                     (self.__housing.mass_L3 * self.__housing.specific_heat_L3)
            equation_rhs_array = [d_by_dt_battery_temperature, d_by_dt_system_air_temperature, d_by_dt_L1_temperature,
                                  d_by_dt_L3_temperature]
            return equation_rhs_array

        try:
            sol = solve_ivp(equation_rhs, (0, self.sample_time),
                            [self.__battery_temperature, self.__system_air_temperature, self.__housing.surface_temperature_L1,
                             self.__housing.surface_temperature_L3], t_eval=np.linspace(0, self.sample_time, num=int(self.sample_time)))
            temperature_series = sol.y
            self.__battery_temperature = temperature_series[0, -1]
            self.__system_air_temperature = temperature_series[1, -1]
            self.__housing.surface_temperature_L1 = temperature_series[2, -1]
            self.__housing.surface_temperature_L3 = temperature_series[3, -1]
        except ValueError as err:
            self.__log.error(err)

        # update states
        self.__storage_technology.state.temperature = self.__battery_temperature

    def get_auxiliaries(self) -> [Auxiliary]:
        return [self.__heating_cooling]

    def get_temperature(self) -> float:
        return self.__system_air_temperature

    def get_ambient_temperature(self) -> float:
        return 0.0

    def get_solar_irradiation_thermal_load(self) -> float:
        return 0.0

    def get_hvac_thermal_power(self) -> float:
        return 0.0

    def reset_profiles(self, ts_adapted: float) -> None:
        """
        Enables looping of the simulation beyond the original length of the time series for the AmbientThermalModel and
        SolarIrradiationModel
        """
        pass

        # def get_air_mass(self) -> float:
    #     return self.__air_mass
    #
    # def get_air_specific_heat(self) -> float:
    #     return self.__air_specific_heat

    def close(self):
        self.__housing.close()
        self.__log.close()
