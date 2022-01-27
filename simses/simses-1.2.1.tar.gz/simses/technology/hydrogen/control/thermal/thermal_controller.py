from abc import ABC, abstractmethod


class ThermalController(ABC):
    """ This controller controls the temperature of the EL-stack by setting new values for the mass flow and the
    temperature of the water running through the stack. It is asumed that the water temperature coming out of the
    stack equals the stack temperature"""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def calculate(self, stack_temperature: float, heat_stack: float, timestep: float, current_dens: float) -> None:
        pass

    @abstractmethod
    def get_heat_control_on(self) -> bool:
        pass

    @abstractmethod
    def get_h2o_flow(self) -> float:
        pass

    @abstractmethod
    def get_delta_water_temp_in(self) -> float:
        pass
