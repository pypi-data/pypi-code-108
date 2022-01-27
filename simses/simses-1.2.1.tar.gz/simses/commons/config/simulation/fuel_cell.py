from configparser import ConfigParser

from simses.commons.config.simulation.simulation_config import SimulationConfig


class FuelCellConfig(SimulationConfig):
    """
    Fuel cell specific configs
    """

    def __init__(self, config: ConfigParser, path: str = None):
        super().__init__(path, config)
        self.__section: str = 'FUEL_CELL'

    @property
    def eol(self) -> float:
        """Returns end of life criterion from data_config file_name"""
        return float(self.get_property(self.__section, 'EOL'))

    @property
    def pressure_cathode(self) -> float:
        """Retruns desired pressure of cathode of electrolyzer"""
        return float(self.get_property(self.__section, 'PRESSURE_CATHODE'))

    @property
    def pressure_anode(self) -> float:
        """Retruns desired pressure of cathode of electrolyzer"""
        return float(self.get_property(self.__section, 'PRESSURE_ANODE'))

    @property
    def temperature(self) -> float:
        """Retruns desired pressure of cathode of electrolyzer"""
        return float(self.get_property(self.__section, 'TEMPERATURE'))
