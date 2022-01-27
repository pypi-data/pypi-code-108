from simses.commons.config.simulation.electrolyzer import ElectrolyzerConfig
from simses.commons.constants import Hydrogen
from simses.technology.hydrogen.control.thermal.thermal_controller import ThermalController


class IdealVarFlowThermalController(ThermalController):
    """
    This controller controls the temperature of the EL-stack by varing the input temperaure of the feeding water and
    in the second step adapt the mass flow of the water in order to reach the desired temperature
    """

    def __init__(self, config: ElectrolyzerConfig, heat_capacity_stack: float):
        super().__init__()
        self.__stack_temp_desire = config.desire_temperature  # °C
        self.__heat_capacity_stack = heat_capacity_stack  # J/K
        self.__delta_water_temperature = 5  # K
        self.__max_temperature_variation_rate = 1 / 60  #  K/s from: "Current status of water electrolysis for energy storage, grid balancing and sector coupling via power-to-gas and power-to-liquids: A review"
        self.__heat_desire = 0  # W
        self.__delta_water_temp_in = 0  # °C
        self.__h2o_flow = 0  # mol/s
        self.__current_dens_zero_counter = 0
        self.__shut_down_time = 0.5  # h
        self.__heat_control_on: bool = False
        self.__heat_h2o_calculated = 0

    def calculate(self, stack_temperature: float, heat_stack: float, timestep: float, current_dens: float) -> None:
        temp_diff = self.__stack_temp_desire - stack_temperature
        ideal_temp_variation_rate = temp_diff / timestep  # K/s
        if abs(ideal_temp_variation_rate) < abs(self.__max_temperature_variation_rate):
            temp_var_rate = ideal_temp_variation_rate
        else:
            temp_var_rate = ideal_temp_variation_rate / abs(ideal_temp_variation_rate) * self.__max_temperature_variation_rate
        self.__heat_desire = temp_var_rate * self.__heat_capacity_stack  # J/s
        self.__heat_control_on = self.check_control_status(current_dens, timestep)
        heat_water = self.__heat_desire - heat_stack
        if self.__heat_control_on:
            if heat_water > 0:  # stack needs to be heated
                self.__delta_water_temp_in = self.__delta_water_temperature  # K
                self.__h2o_flow = heat_water / (Hydrogen.HEAT_CAPACITY_WATER *
                                                Hydrogen.MOLAR_MASS_WATER * self.__delta_water_temp_in)  # mol/s
            elif heat_water < 0:  # stack needs to be cooled
                self.__delta_water_temp_in = - self.__delta_water_temperature  # K
                self.__h2o_flow = heat_water / (Hydrogen.HEAT_CAPACITY_WATER *
                                                Hydrogen.MOLAR_MASS_WATER * self.__delta_water_temp_in)  # mol/s
            else:
                self.__delta_water_temp_in = 0  # K
                self.__h2o_flow = 0  # mol/s
        else:
            self.__delta_water_temp_in = 0  # °K
            self.__h2o_flow = 0  # mol/s

    def check_control_status(self, current_dens, timestep) -> bool:
        if current_dens == 0:
            self.__current_dens_zero_counter += 1
        else:
            self.__current_dens_zero_counter = 0
        if self.__current_dens_zero_counter <= self.__shut_down_time * 3600 / timestep:
            return True
        else:
            return False

    def get_heat_control_on(self) -> bool:
        return self.__heat_control_on

    def get_delta_water_temp_in(self) -> float:
        return self.__delta_water_temp_in

    def get_h2o_flow(self) -> float:
        return self.__h2o_flow
