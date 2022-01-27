from simses.commons.config.simulation.electrolyzer import ElectrolyzerConfig
from simses.technology.hydrogen.control.pressure.pressure_controller import \
    PressureController


class IdealVarCathodePressureController(PressureController):
    """ This pressure controller controls the cathode pressure at a disired level and keeps the anode pressure
    at ambient level"""
    def __init__(self, config: ElectrolyzerConfig):
        super().__init__()
        self.__max_pressure_variation_rate: float = 0.5  # bar/s
        self.__pressure_control_on: bool = False
        self.__no_h2_production_counter: float = 0
        self.__shut_down_time: float = 0.5  # h
        self.__pressure_cathode_desire: float = config.desire_pressure_cathode
        self.__pressure_anode_desire: float = config.desire_pressure_anode

    def calculate_n_h2_out(self, pressure_cathode, n_h2_prod, timestep, pressure_factor) -> float:
        """
        calculates the necessary hydrogen outflow to reach the desire pressure relative to the actual hydrogen
        production and cathode pressure

        input: pressure cathode in barg, pressure cathode desire in barg, h2 production in mol/s, timestep in s,
        pressure factor in bar/mol

        output: h2 outflow in mol/s
        """
        delta_pressure = self.__pressure_cathode_desire - pressure_cathode  # bar
        pressure_variation_rate_desire = delta_pressure / timestep  # bar/s  >0 if pressure cathode > pressure cathode deisire
        self.__pressure_control_on = self.__check_pressure_control_on(n_h2_prod, timestep)
        if self.__pressure_control_on:  # control is on -> pressure value is kept at its desire value
            if abs(pressure_variation_rate_desire) < self.__max_pressure_variation_rate:
                pressure_variation_rate = pressure_variation_rate_desire
            else:
                pressure_variation_rate = pressure_variation_rate_desire / abs(pressure_variation_rate_desire) * self.__max_pressure_variation_rate
            # p_c_1 = pressure_cathode + pressure_variation_rate * timestep
            n_h2_out = n_h2_prod - pressure_variation_rate / pressure_factor
            return max(n_h2_out, 0)
        else:
            p_c_1 = max(pressure_cathode - self.__max_pressure_variation_rate * timestep, 0)
            return n_h2_prod - (p_c_1 - pressure_cathode) / (pressure_factor * timestep)

    def calculate_n_o2_out(self, pressure_anode: float, n_o2_prod: float, timestep: float) -> float:
        if n_o2_prod >= 0:
            return n_o2_prod
        else:
            return 0  # no intake of atmosphere in case of negative oxygen production (-> only permeation)

    def __check_pressure_control_on(self, n_h2_prod: float, timestep: float) -> bool:
        if n_h2_prod <= 0:
            self.__no_h2_production_counter += 1
        else:
            self.__no_h2_production_counter = 0
        if self.__no_h2_production_counter <= self.__shut_down_time * 3600 / timestep:
            return True
        else:
            return False

    def calculate_n_h2_in(self, pressure_anode: float, n_h2_used: float) -> float:
        return n_h2_used

    def calculate_n_o2_in(self, pressure_cathode: float, n_o2_used: float) -> float:
        return n_o2_used
