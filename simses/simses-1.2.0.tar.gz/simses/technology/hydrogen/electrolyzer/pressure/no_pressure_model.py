from simses.commons.state.technology.electrolyzer import ElectrolyzerState
from simses.technology.hydrogen.control.pressure.no_pressure_controller import NoPressureController
from simses.technology.hydrogen.electrolyzer.pressure.abstract_model import PressureModel


class NoPressureModel(PressureModel):

    def __init__(self):
        super().__init__()
        self.__pressure_cathode_el = 0  # barg
        self.__pressure_anode_el = 0  # barg
        self.__pressure_cathode_desire_el = 0  # barg
        self.__pressure_anode_desire_el = 0  # barg
        self.__hydrogen_outflow = 0  # mol/s
        self.__oxygen_outflow = 0  # mol/s
        self.pressure_controller = NoPressureController()

    def calculate(self, time, state: ElectrolyzerState) -> None:
        self.__pressure_anode_el = state.pressure_anode
        self.__pressure_cathode_el = state.pressure_cathode
        hydrogen_produced = state.hydrogen_production
        oxygen_produced = state.oxygen_production
        self.__hydrogen_outflow = self.pressure_controller.calculate_n_h2_out(self.__pressure_cathode_el, self.__pressure_cathode_desire_el, hydrogen_produced, 0)
        self.__oxygen_outflow = self.pressure_controller.calculate_n_o2_out(self.__pressure_anode_el, self.__pressure_anode_desire_el, oxygen_produced)

    def get_pressure_anode(self) -> float:
        return self.__pressure_anode_el

    def get_pressure_cathode(self) -> float:
        return self.__pressure_cathode_el

    def get_h2_outflow(self) -> float:
        return self.__hydrogen_outflow

    def get_o2_outflow(self) -> float:
        return self.__oxygen_outflow

    def get_h2o_outflow_cathode(self) -> float:
        return 0

    def get_h2o_outflow_anode(self) -> float:
        return 0
