from abc import abstractmethod

from simses.system.auxiliary.auxiliary import Auxiliary

class Compressor(Auxiliary):
    """ Compressor is an auxiliary. It calculates the necessary electric power in W which is needed to compress an ideal gas
    from pressure 1 to pressure 2"""

    def __init__(self):
        super().__init__()

    def ac_operation_losses(self) -> float:
        """
        Calculates the ac operation losses

        Parameters
        ----------

        :returns
        -------
        float:
            Power in W
        """
        return self.get_compression_power()

    @abstractmethod
    def calculate_compression_power(self, hydrogen_flow_out:float, pressure_1: float, pressure_2: float, temperature: float) -> None:
        """
        Calculates the compression power

        :returns
        -------

        """
        pass

    @abstractmethod
    def get_compression_power(self) -> float:
        """
        Gets compressor power in W

        :returns
        --------

        """
        pass
