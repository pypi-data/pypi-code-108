from configparser import ConfigParser

from simses.commons.config.simulation.simulation_config import SimulationConfig


class RedoxFlowConfig(SimulationConfig):
    """
    Redox Flow specific configs
    """

    def __init__(self, config: ConfigParser, path: str = None):
        super().__init__(path, config)
        self.__section: str = 'REDOX_FLOW'

    @property
    def soc(self) -> float:
        """Returns start soc for rfb from __analysis_config file_name"""
        return float(self.get_property(self.__section, 'START_SOC'))

    @property
    def min_soc(self) -> float:
        """Returns min soc for rfb from __analysis_config file_name"""
        return float(self.get_property(self.__section, 'MIN_SOC'))

    @property
    def max_soc(self) -> float:
        """Returns max soc for rfb from __analysis_config file_name"""
        return float(self.get_property(self.__section, 'MAX_SOC'))

    @property
    def exact_size(self) -> bool:
        """Returns selection for exact sizing True/False"""
        return self.get_property(self.__section, 'EXACT_SIZE') in ['True']
