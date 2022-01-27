from simses.commons.config.simulation.electrolyzer import ElectrolyzerConfig
from simses.commons.state.technology.electrolyzer import ElectrolyzerState
from simses.technology.hydrogen.control.pressure.no_pressure_controller import NoPressureController
from simses.technology.hydrogen.electrolyzer.pressure.abstract_model import PressureModel


class AlkalinePressureModel(PressureModel):

    def __init__(self, config: ElectrolyzerConfig):
        super().__init__()
        self.__pressure_cathode_el = config.desire_pressure_cathode  # barg
        self.__pressure_anode_el = config.desire_pressure_anode  # barg
        if self.__pressure_cathode_el != self.__pressure_anode_el:
            raise Exception('Current alkaline electrolzyer assumes same pressure on cathode and anode. '
                            'Please check your config.')
        self.__pressure_cathode_desire_el = config.desire_pressure_cathode  # barg
        self.__pressure_anode_desire_el = config.desire_pressure_anode  # barg
        self.__hydrogen_outflow = 0  # mol/s
        self.__oxygen_outflow = 0  # mol/s
        self.__pressure_controller = NoPressureController()

    def calculate(self, time, state: ElectrolyzerState) -> None:
        # Express anode/cathode pressure relative to atmospheric pressure, for implementation with existing hydrogen storage model
        # self.__pressure_anode_el: float = state.pressure_anode - 1     # in barg
        # self.__pressure_cathode_el: float = state.pressure_cathode - 1   # in barg
        hydrogen_produced = state.hydrogen_production
        oxygen_produced = state.oxygen_production
        self.__hydrogen_outflow = self.__pressure_controller.calculate_n_h2_out(self.__pressure_cathode_el, self.__pressure_cathode_desire_el, hydrogen_produced, 0)
        self.__oxygen_outflow = self.__pressure_controller.calculate_n_o2_out(self.__pressure_anode_el, self.__pressure_anode_desire_el, oxygen_produced)

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
