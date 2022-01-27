from simses.commons.state.system import SystemState
from simses.system.auxiliary.auxiliary import Auxiliary
from simses.system.dc_coupling.generation.dc_generation import DcGeneration
from simses.system.dc_coupling.load.dc_load import DcLoad


class DcCoupling:

    """
    DcCouplings provide a possiblity to add a DC load or DC generation to the intermediate circuit of an AC storage
    system.
    """

    def __init__(self, dc_load: DcLoad, dc_generation: DcGeneration):
        self.__dc_load: DcLoad = dc_load
        self.__dc_generation: DcGeneration = dc_generation

    def update(self, time: float, state: SystemState) -> None:
        """
        In-place update of system state for dc power additional

        Parameters
        ----------
        time :
            current timestamp in s
        state :
            current system state
        """
        self.__dc_load.calculate_power(time)
        self.__dc_generation.calculate_power(time)
        state.dc_power_additional += self.get_power()

    def get_power(self) -> float:
        """

        Returns
        -------
        float:
            net power of DC load and DC generation in W
        """
        return self.__dc_generation.get_power() - self.__dc_load.get_power()

    def get_auxiliaries(self) -> [Auxiliary]:
        auxiliaries: [Auxiliary] = list()
        auxiliaries.extend(self.__dc_load.get_auxiliaries())
        auxiliaries.extend(self.__dc_generation.get_auxiliaries())
        return auxiliaries

    def close(self):
        self.__dc_load.close()
        self.__dc_generation.close()
