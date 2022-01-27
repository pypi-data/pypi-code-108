from abc import ABC, abstractmethod


class PressureController(ABC):
    """ This controller controls the pressure of anode and cathode side of the electrolyzer like a control valve"""
    def __init__(self):
        super().__init__()

    @abstractmethod
    def calculate_n_h2_out(self, pressure_cathode: float, n_h2_prod: float, timestep: float, pressure_factor: float) -> float:
        pass

    @abstractmethod
    def calculate_n_o2_out(self, pressure_anode: float, n_o2_prod: float, timestep: float) -> float:
        pass

    @abstractmethod
    def calculate_n_h2_in(self, pressure_anode: float, n_h2_used: float) -> float:
        pass

    @abstractmethod
    def calculate_n_o2_in(self, pressure_cathode: float, n_o2_used: float) -> float:
        pass
