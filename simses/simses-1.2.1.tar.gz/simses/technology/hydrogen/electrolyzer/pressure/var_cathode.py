from simses.commons.config.simulation.electrolyzer import ElectrolyzerConfig
from simses.commons.constants import Hydrogen
from simses.commons.state.technology.electrolyzer import ElectrolyzerState
from simses.technology.hydrogen.control.pressure.ideal_var_cathode import \
    IdealVarCathodePressureController
from simses.technology.hydrogen.electrolyzer.pressure.abstract_model import PressureModel
from simses.technology.hydrogen.electrolyzer.stack.stack_model import ElectrolyzerStackModel


class VarCathodePressureModel(PressureModel):

    def __init__(self, electrolyzer: ElectrolyzerStackModel, config: ElectrolyzerConfig):
        super().__init__()
        nominal_stack_power: float = electrolyzer.get_nominal_stack_power()
        self.VOLUME_GAS_SEPARATOR = 0.4225 * 10 ** (-3) * nominal_stack_power / 1000.0  # dm³ -> m³  0.4425 l/kW: value for Volume from H-TEC Series-ME: ME 450/1400
        self.__pressure_controller = IdealVarCathodePressureController(config)
        self.__p_c_1 = 0  # barg
        self.__p_a_1 = 0  # barg
        self.__n_h2_out_c = 0  # mol  mass which is set free through the control valve at cathode side
        self.__n_o2_out_a = 0  # mol  mass which is set free through the control valve at anode side
        self.__h2_outflow = 0  # mol/s
        self.__o2_outflow = 0  # mol/s
        self.__h2o_ouflow_cathode = 0  # mol/s
        self.__h2o_outflow_anode = 0  # mol/s

    def calculate(self, time, state: ElectrolyzerState):
        timestep = time - state.time
        stack_temp = state.temperature + 273.15  # °C -> K
        p_c_0 = state.pressure_cathode  # barg
        p_a_0 = state.pressure_anode  # barg
        p_h2o_0 = state.sat_pressure_h2o  # bar
        n_h2_prod = state.hydrogen_production  # mol/s at stack level
        x_h2o_c = p_h2o_0 / (1 + p_c_0 - p_h2o_0)
        n_o2_prod = state.oxygen_production  # mol/s at stack level
        x_h2o_a = p_h2o_0 / (1 + p_a_0 - p_h2o_0)
        pressure_factor_cathode = Hydrogen.IDEAL_GAS_CONST * stack_temp / self.VOLUME_GAS_SEPARATOR * \
                                  (1 + x_h2o_c) * 10 ** (-5)  # bar/mol   transfer from Pa to bar with 1bar 0 10^5 Pa = 10^5 N/m²
        self.__n_h2_out_c = self.__pressure_controller.calculate_n_h2_out(p_c_0, n_h2_prod, timestep, pressure_factor_cathode)
        self.__n_o2_out_a = self.__pressure_controller.calculate_n_o2_out(p_a_0, n_o2_prod, timestep)

        # new pressure cathode
        self.__p_c_1 = p_c_0 + pressure_factor_cathode * (n_h2_prod - self.__n_h2_out_c) * timestep  # bar

        # new pressure anode
        # self.p_a_1 = p_a_0 + ConstantsHydrogen.IDEAL_GAS_CONST * stack_temp / self.VOLUME_GAS_SEPARATOR * (1 + x_h2o_a) * \
        #              (n_o2_prod - self.n_o2_out_a) * 10 ** (-5)  # bar
        self.__p_a_1 = p_a_0

        # outflow rates of h2, o2 and h2o
        self.__h2_outflow = self.__n_h2_out_c  # mol/s
        self.__o2_outflow = self.__n_o2_out_a  # mol/s
        self.__h2o_ouflow_cathode = x_h2o_c * self.__h2_outflow  # mol/s
        self.__h2o_outflow_anode = x_h2o_a * self.__o2_outflow  # mol/s

    def get_pressure_cathode(self) -> float:
        return self.__p_c_1

    def get_pressure_anode(self) -> float:
        return self.__p_a_1

    def get_h2_outflow(self) -> float:
        return self.__h2_outflow

    def get_o2_outflow(self) -> float:
        return self.__o2_outflow

    def get_h2o_outflow_cathode(self) -> float:
        return self.__h2o_ouflow_cathode

    def get_h2o_outflow_anode(self) -> float:
        return self.__h2o_outflow_anode
