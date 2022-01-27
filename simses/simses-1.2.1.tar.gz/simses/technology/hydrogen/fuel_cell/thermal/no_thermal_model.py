from simses.commons.state.technology.fuel_cell import FuelCellState
from simses.technology.hydrogen.fuel_cell.thermal.thermal_model import ThermalModel


class NoThermalModel(ThermalModel):
    """This model functions at the Storage Technology Level.
      This model treats the entire Storage Technology as 1 lump.
      Current version sets temperature of Storage Technology to 298.15 K and treats it as constant"""

    def __init__(self):
        super().__init__()
        self.__temperature = 298.15 # K

    def calculate(self, time, state: FuelCellState) -> None:
        self.__temperature = state.temperature

    def get_temperature(self) -> float:
        return self.__temperature

    def get_pump_power(self) -> float:
        return 0.0

    def get_water_flow_stack(self) -> float:
        return 0.0

    def get_power_water_heating(self) -> float:
        return 0.0
