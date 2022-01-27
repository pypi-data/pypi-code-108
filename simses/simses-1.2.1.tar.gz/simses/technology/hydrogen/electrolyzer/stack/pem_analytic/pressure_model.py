from simses.commons.state.technology.electrolyzer import ElectrolyzerState


class PemPressureModel:

    A_CATHODE = 2.4  # bar cm²/A
    A_ANODE = 2.8  # bar cm²/A

    def __init__(self, parameters):
        self.__parameters = parameters
        #self.__sat_pressure_h2o: float = 0.03189409713071401  # bar
        #self.__part_pressure_h2: float = 1.0 - self.__sat_pressure_h2o  # bar
        #self.__part_pressure_o2: float = 1.0 - self.__sat_pressure_h2o  # bar

    def get_sat_pressure_h2o(self, stack_temperature: float) -> float:
            return self.__get_sat_pressure_h2o(stack_temperature)

    def get_sat_pressure_h2o_for_current_calc(self, stack_temperature: float):
        return self.__get_sat_pressure_h2o(stack_temperature, self.__parameters.q10, self.__parameters.q11,
                                           self.__parameters.q12, self.__parameters.q13, self.__parameters.q14)

    def __get_sat_pressure_h2o(self, stack_temperature: float, q10: float=1, q11: float=1, q12: float=1, q13: float=1,
                               q14: float=1) -> float:
        """ stack temperature needs to be in °C """
        return q10 * 10 ** (- q11 * 2.1794 + q12 * 0.02953 *
                           stack_temperature - q13 * 9.1837 * 10 ** (-5) *
                           stack_temperature ** 2 + q14 * 1.4454 * 10 ** (-7) *
                           stack_temperature ** 3)  # bar saturation pressure of water

    def get_partial_pressure_h2_for_current_calc(self, state: ElectrolyzerState, current_dens_cell: float):
        return self.__get_partial_pressure_h2(state.pressure_cathode, current_dens_cell,
                                              self.get_sat_pressure_h2o_for_current_calc(state.temperature),
                                              self.__parameters.q15)

    def get_partial_pressure_h2(self, state: ElectrolyzerState, current_dens_cell: float):
        return self.__get_partial_pressure_h2(state.pressure_cathode, current_dens_cell,
                                              self.get_sat_pressure_h2o(state.temperature))

    def __get_partial_pressure_h2(self, p_cathode: float, current_dens_cell: float, sat_pressure_h2o: float,
                                  q11: float=1) -> float:
        return (1 + q11 * p_cathode) - sat_pressure_h2o + self.A_CATHODE * current_dens_cell # bar

    def get_partial_pressure_o2_for_current_calc(self, state: ElectrolyzerState, current_dens_cell: float):
        return self.__get_partial_pressure_o2(state.pressure_anode, current_dens_cell,
                                              self.get_sat_pressure_h2o_for_current_calc(state.temperature),
                                              self.__parameters.q9)

    def get_partial_pressure_o2(self, state: ElectrolyzerState, current_dens_cell: float):
         return self.__get_partial_pressure_o2(state.pressure_anode, current_dens_cell,
                                               self.get_sat_pressure_h2o(state.temperature))

    def __get_partial_pressure_o2(self, p_anode: float, current_dens_cell: float, sat_pressure_h2o: float,
                                  q12: float=1) -> float:
        return (1 + q12 * p_anode) - sat_pressure_h2o + self.A_ANODE * current_dens_cell  # bar
