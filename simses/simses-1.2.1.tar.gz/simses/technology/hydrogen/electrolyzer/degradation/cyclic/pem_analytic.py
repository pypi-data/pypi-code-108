from simses.commons.state.technology.electrolyzer import ElectrolyzerState
from simses.technology.hydrogen.electrolyzer.degradation.cyclic.cyclic_degradation import \
    CyclicDegradationModel


class CyclicDegradationPemElMultiDimAnalytic(CyclicDegradationModel):

    def __init__(self):
        super().__init__()
        self.__resistance_increase = 0
        self.__exchange_current_dens_decrease = 0  # p.u.
        self.__current_zero_counter = 0  # counts timesteps since begin of current = 0

    def calculate_resistance_increase(self, time: float, state: ElectrolyzerState) -> None:
        """
        Calculation of resistance increase dependent on currentdensity provided to the electrolyzer cell
        recovery effect: all time exponential
        based on paper: "Polymer electrolyte membrane water electrolysis: Restraining degradation in the presence
        of fluctuating power"  by Rakousky, Christoph
        year: 2017
        :param time:
        :param state:
        :return: none
        """
        timestep = time - state.time
        current_dens = state.current_density
        if current_dens == 0:  # recovery effect: all time exponential
            self.__current_zero_counter += 1
            time = self.__current_zero_counter * timestep / 3600  # s -> h
            # self.__resistance_increase = - 1.968 * 10 ** (-4) * 0.4263 * np.exp(0.4263 * time) * timestep / 3600  # exponential recovery of total resistance
            self.__resistance_increase = (- 2 * 5.151 * 10 ** (-5) * time - 7.991 * 10 ** (-5)) * timestep / 3600  # quadratic recovery of total resistance
        elif 0 < current_dens < 1:
            self.__current_zero_counter = 0
            self.__resistance_increase = 0
        elif current_dens > 1:
            self.__current_zero_counter = 0
            self.__resistance_increase = 3.89 * 10 ** (-4) * (current_dens-1) * timestep / 3600  # p.u.
        else:
            self.__current_zero_counter = 0
            self.__resistance_increase = 0  # p.u.

    def calculate_exchange_current_dens_decrerase(self, state: ElectrolyzerState):
        """ No cyclic exchange_current_density_decrease """
        self.__exchange_current_dens_decrease = 0

    def get_resistance_increase(self) -> float:
        return self.__resistance_increase

    def get_exchange_current_dens_decrease(self) -> float:
        return self.__exchange_current_dens_decrease

    def reset(self, hydrogen_state: ElectrolyzerState) -> None:
        pass

    def close(self) -> None:
        pass

    # def calculate_resistance_increase(self, time: float, hydrogen_state: HydrogenState) -> None:
    #     """
    #     Calculation of resistance increase dependent on currentdensity provided to the electrolyzer cell
    #     recovery effect: first 6h exponential, afterwards linear
    #     based on paper: "Polymer electrolyte membrane water electrolysis: Restraining degradation in the presence
    #     of fluctuating power"  by Rakousky, Christoph
    #     year: 2017
    #     :param time:
    #     :param hydrogen_state:
    #     :return: none
    #     """
    #     time_passed = time - hydrogen_state.time
    #     current_dens = hydrogen_state.current_density_el
    #     if current_dens == 0:
    #         if time_passed / 3600 <= 6:  # recovery effect: exponential
    #             self.__current_zero_counter += 1
    #             time = self.__current_zero_counter * time_passed / 3600  # s -> h
    #             self.__resistance_increase = - 1.968 * 10 ** (-4) * 0.4263 * np.exp(0.4263 * time) * time_passed / 3600  # exponential recovery of total resistance
    #         else:  # recovery effect: linear, with slop of exponentail recovery at time=6h
    #             self.__resistance_increase = -1.0828763 * 10 ** (-3) * time_passed / 3600
    #     elif current_dens > 0 and current_dens <= 1:
    #         self.__current_zero_counter = 0
    #         self.__resistance_increase = 0  # p.u.
    #     elif current_dens >= 1 and current_dens < 2:
    #         self.__current_zero_counter = 0
    #         self.__resistance_increase = 2.083 * 10 ** (-4) * time_passed / 3600  # p.u.
    #     elif current_dens >= 2:
    #         self.__current_zero_counter = 0
    #         self.__resistance_increase = 3.89 * 10 ** (-4) * time_passed / 3600  # p.u.
    #     else:
    #         self.__current_zero_counter = 0
    #         self.__resistance_increase = 0  # p.u.



