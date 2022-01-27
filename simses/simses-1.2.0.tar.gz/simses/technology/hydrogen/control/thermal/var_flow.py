from simses.commons.config.simulation.electrolyzer import ElectrolyzerConfig
from simses.commons.constants import Hydrogen
from simses.technology.hydrogen.control.thermal.thermal_controller import ThermalController


class VarFlowThermalController(ThermalController):
    """
    This controller controls the temperature of the EL-stack by varing the input temperaure of the feeding water and
    in the second step adapt the mass flow of the water in order to reach the desired temperature
    """

    def __init__(self, config: ElectrolyzerConfig, min_water_flow_stack: float, heat_capacity: float):
        super().__init__()
        self.__stack_temp_desire = config.desire_temperature # °C
        self.__slope_faktor = - 1 / 5
        self.__delta_water_temperature = 5  # K
        self.__max_cooling_rate = 3  # K/s; assumption needs to be that high, so that there is no thermal runaway
        self.__temperature_h2o_in = 0  # °C
        self.__h2o_flow = 0  # mol/s#
        self.__min_water_flow_stack: float = min_water_flow_stack
        self.__heat_capacity: float = heat_capacity

    def calculate(self, stack_temperature: float, heat_stack: float, timestep: float, current_dens: float) -> None:
        temp_diff = self.__stack_temp_desire - stack_temperature
        # calculation of water temperature
        control_faktor = self.__calculate_control_faktor_temperature(temp_diff)
        self.__temperature_h2o_in = stack_temperature - control_faktor * self.__delta_water_temperature
        # calculation of water flow
        if stack_temperature <= self.__stack_temp_desire:
            self.__h2o_flow = self.__min_water_flow_stack
        else:
            ideal_cooling_rate = temp_diff / timestep
            if ideal_cooling_rate < self.__max_cooling_rate:
                cooling_rate = ideal_cooling_rate
            else:
                cooling_rate = self.__max_cooling_rate
            self.__h2o_flow = self.__heat_capacity * cooling_rate / (Hydrogen.HEAT_CAPACITY_WATER *
                                                                     Hydrogen.MOLAR_MASS_WATER * temp_diff)

    def get_delta_water_temp_in(self) -> float:
        return self.__temperature_h2o_in

    def get_h2o_flow(self) -> float:
        return self.__h2o_flow

    def __calculate_control_faktor_temperature(self, temp_diff) -> float:
        if abs(temp_diff) < 5:
            return self.__slope_faktor * temp_diff
        else:
            return 1.0
