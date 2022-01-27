from simses.commons.state.technology.fuel_cell import FuelCellState
from simses.technology.hydrogen.control.pressure.no_pressure_controller import NoPressureController
from simses.technology.hydrogen.fuel_cell.pressure.pressure_model import PressureModel


class NoPressureModel(PressureModel):

    def __init__(self):
        super().__init__()
        self.__pressure_cathode = 0  # barg
        self.__pressure_anode = 0  # barg
        self.__pressure_cathode_desire = 0  # barg
        self.__pressure_anode_desire = 0  # barg
        self.__hydrogen_inflow = 0  # mol/s
        self.__oxygen_inflow = 0  # mol/s
        self.__pressure_controller = NoPressureController()

    def calculate(self, time, state: FuelCellState) -> None:
        self.__pressure_anode = state.pressure_anode
        self.__pressure_cathode = state.pressure_cathode
        hydrogen_used = state.hydrogen_use
        oxygen_used = state.oxygen_use
        self.__hydrogen_inflow = self.__pressure_controller.calculate_n_h2_in(self.__pressure_anode, hydrogen_used)
        self.__oxygen_inflow = self.__pressure_controller.calculate_n_o2_in(self.__pressure_cathode, oxygen_used)

    def get_pressure_cathode_fc(self) -> float:
        return self.__pressure_cathode

    def get_pressure_anode_fc(self) -> float:
        return self.__pressure_anode

    def get_h2_inflow(self) -> float:
        return self.__hydrogen_inflow

    def get_o2_inflow(self) -> float:
        return self.__oxygen_inflow


