from simses.commons.state.technology.electrolyzer import ElectrolyzerState
from simses.technology.hydrogen.electrolyzer.degradation.cyclic.cyclic_degradation import \
    CyclicDegradationModel


class CyclicDegradationPemElMultiDimAnalyticPtlCoating(CyclicDegradationModel):

    """ Anode Ti-PTL of Electrolyzer cell is coated with thin Pt. This avoids the cyclic degradation of the
     resistance. Therefore this degradation model does not have cyclic degradation. """

    def __init__(self):
        super().__init__()
        self.__resistance_increase = 0
        self.__exchange_current_dens_decrease = 0  # p.u.
        self.__current_zero_counter = 0  # counts timesteps since begin of current = 0

    def calculate_resistance_increase(self, time: float, state: ElectrolyzerState) -> None:
       """" No cyclic resistance increase """
       self.__resistance_increase = 0

    def calculate_exchange_current_dens_decrerase(self, state: ElectrolyzerState):
        """ No cyclic exchange_current_density_decrease """
        self.__exchange_current_dens_decrease = 0

    def get_resistance_increase(self) -> float:
        return self.__resistance_increase

    def get_exchange_current_dens_decrease(self) -> float:
        return self.__exchange_current_dens_decrease

    def reset(self, state: ElectrolyzerState) -> None:
        pass

    def close(self) -> None:
        pass



