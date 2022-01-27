from abc import ABC, abstractmethod

from simses.commons.state.technology.fuel_cell import FuelCellState


class ThermalModel(ABC):

    def __init__(self):
        super().__init__()

    def update(self, time: float, state: FuelCellState) -> None:
        """Updating temperature of electrolyzer stack in hydrogen state"""
        self.calculate(time, state)
        state.temperature = self.get_temperature()
        state.water_flow_fc = self.get_water_flow_stack()

    @abstractmethod
    def calculate(self, time: float, state: FuelCellState) -> None:
        pass

    @abstractmethod
    def get_temperature(self) -> float:
        pass

    @abstractmethod
    def get_water_flow_stack(self) -> float:
        pass

    @abstractmethod
    def get_power_water_heating(self) -> float:
        pass

    @abstractmethod
    def get_pump_power(self) -> float:
        pass

    def close(self) -> None:
        """Closing all resources in thermal model"""
        pass
