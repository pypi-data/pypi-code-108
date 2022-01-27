from simses.commons.state.technology.electrolyzer import ElectrolyzerState
from simses.technology.hydrogen.electrolyzer.thermal.abstract_model import ThermalModel


class NoThermalModel(ThermalModel):
    """This model functions at the Storage Technology Level.
      This model treats the entire Storage Technology as 1 lump.
      Current version sets temperature of Storage Technology to 298.15 K and treats it as constant"""

    def __init__(self):
        super().__init__()
        self.__temperature = 80  # °C

    def calculate(self, time, state: ElectrolyzerState, pressure_cathode_0, pressure_anode_0) -> None:
        pass

    def get_temperature(self) -> float:
        return self.__temperature

    def get_water_flow_stack(self) -> float:
        return 0.0

    def get_power_water_heating(self) -> float:
        return 0.0

    def calculate_pump_power(self, water_flow_stack: float) -> None:
        pass

    def get_pump_power(self) -> float:
        return 0.0

    def get_convection_heat(self) -> float:
        return 0.0

    def set_temperature(self, new_temperature: float):
        self.__temperature = new_temperature

    def calculate_tube_pressure_loss(self, water_flow_stack: float) -> None:
        pass

    def get_tube_pressure_loss(self) -> float:
        return 0.0
