from simses.commons.constants import Hydrogen
from simses.system.auxiliary.compression.compressor import Compressor


class HydrogenIsentropCompressor(Compressor):

    def __init__(self, compressor_eta = 0.95):
        super().__init__()
        self.__compressor_eta = compressor_eta
        self.__compression_power = 0  # W
        self.__R = Hydrogen.IDEAL_GAS_CONST

    def calculate_compression_power(self, hydrogen_flow_out:float, pressure_1: float, pressure_2: float, temperature: float) -> None:
        real_gas_faktor = Hydrogen.realgas_factor(pressure_1, pressure_2)
        isentropic_exponent = Hydrogen.isentropic_exponent(pressure_1, pressure_2)
        prefactor = isentropic_exponent / (isentropic_exponent - 1)
        self.__compression_power = 1.0 / self.__compressor_eta * prefactor * self.__R * (temperature + 273.15) * \
                                   real_gas_faktor * (( pressure_2 / pressure_1) ** (1 / prefactor) - 1) * hydrogen_flow_out

    def get_compression_power(self) -> float:
        return self.__compression_power
