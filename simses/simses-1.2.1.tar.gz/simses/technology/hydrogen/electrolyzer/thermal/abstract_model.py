from abc import ABC, abstractmethod

from simses.commons.state.technology.electrolyzer import ElectrolyzerState


class ThermalModel(ABC):

    def __init__(self):
        self.__max_water_flow_stack = 0  # mol/s/cell

    def update(self, time: float, state: ElectrolyzerState, pressure_cathode_0, pressure_anode_0) -> None:
        """Updating temperature of electrolyzer (°C) stack in hydrogen state"""
        self.calculate(time, state, pressure_cathode_0, pressure_anode_0)
        state.water_flow = self.get_water_flow_stack()
        self.calculate_pump_power(state.water_flow)
        # self.calculate_tube_pressure_loss(state.water_flow)
        state.temperature = self.get_temperature()

    @abstractmethod
    def calculate(self, time: float, state: ElectrolyzerState, pressure_cathode_0, pressure_anode_0) -> None:
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
    def calculate_pump_power(self, water_flow_stack: float) -> None:
        pass

    # @abstractmethod
    # def calculate_tube_pressure_loss(self, water_flow_stack: float) -> None:
    #     pass

    @abstractmethod
    def get_pump_power(self) -> float:
        pass

    # @abstractmethod
    # def get_tube_pressure_loss(self) -> float:
    #     pass

    @abstractmethod
    def get_convection_heat(self) -> float:
        pass

    def close(self) -> None:
        """Closing all resources in thermal model"""
        pass
