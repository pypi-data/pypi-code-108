from simses.commons.state.technology.fuel_cell import FuelCellState
from simses.technology.hydrogen.fuel_cell.thermal.thermal_model import ThermalModel


class SimpleThermalModel(ThermalModel):
    """
    Simple Thermal Model with assuming a direct dependency to the fuel cell current based on information of Ballard's
    "Product Manual and Integration Guide Integrating the 1020ACS into a System", 2016
    """

    def __init__(self, temperature: float):
        super().__init__()
        self.__temperature = temperature - 273.15  # K -> C

    def calculate(self, time, state: FuelCellState) -> None:
        self.__temperature = -0.53 * state.current + 26.01

    def get_temperature(self) -> float:
        return self.__temperature

    def get_pump_power(self) -> float:
        return 0.0

    def get_water_flow_stack(self) -> float:
        return 0.0

    def get_power_water_heating(self) -> float:
        return 0.0
