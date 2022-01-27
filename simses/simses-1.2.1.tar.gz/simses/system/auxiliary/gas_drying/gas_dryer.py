from abc import abstractmethod

from simses.system.auxiliary.auxiliary import Auxiliary


class GasDrying(Auxiliary):
    """ GasDrying is an auxiliary. It calculates the energy that is needed for drying the product gas according to the
    specified drying level"""

    def __init__(self):
        super().__init__()

    def ac_operation_losses(self) -> float:
        """
        Calculates the ac operation losses
        :return:
         float:
            Power in W
        """
        return self.get_gas_drying_power()

    @abstractmethod
    def calculate_gas_drying_power(self, pressure_cathode, h2_outflow) -> None:
        pass

    @abstractmethod
    def get_gas_drying_power(self) -> float:
        pass