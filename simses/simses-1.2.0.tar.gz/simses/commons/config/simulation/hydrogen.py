from configparser import ConfigParser

from simses.commons.config.simulation.simulation_config import SimulationConfig


class HydrogenConfig(SimulationConfig):
    """
    Hydrogen storage specific configs
    """

    def __init__(self, config: ConfigParser, path: str = None):
        super().__init__(path, config)
        self.__section: str = 'HYDROGEN'

    @property
    def soc(self) -> float:
        """Returns start soc from data_config file_name"""
        return float(self.get_property(self.__section, 'START_SOC'))

    @property
    def min_soc(self) -> float:
        """Returns min soc from data_config file_name"""
        return float(self.get_property(self.__section, 'MIN_SOC'))

    @property
    def max_soc(self) -> float:
        """Returns max soc from data_config file_name"""
        return float(self.get_property(self.__section, 'MAX_SOC'))

    # @property
    # def eol_electrolyzer(self) -> float:
    #     """Returns end of life criterion from data_config file_name"""
    #     return float(self.get_property(self.__section, 'EOL_ELECTROLYZER'))
    #
    # @property
    # def start_pressure_cathode_el(self) -> float:
    #     """Retruns start pressure of cathode of electrolyzer"""
    #     return float(self.get_property(self.__section, 'START_PRESSURE_CATHODE_ELECTROLYZER'))
    #
    # @property
    # def desire_pressure_cathode_el(self) -> float:
    #     """Retruns desired pressure of cathode of electrolyzer"""
    #     return float(self.get_property(self.__section, 'DESIRE_PRESSURE_CATHODE_ELECTROLYZER'))
    #
    # @property
    # def start_pressure_anode_el(self) -> float:
    #     """Retruns start pressure of cathode of electrolyzer"""
    #     return float(self.get_property(self.__section, 'START_PRESSURE_ANODE_ELECTROLYZER'))
    #
    # @property
    # def desire_pressure_anode_el(self) -> float:
    #     """Retruns desired pressure of cathode of electrolyzer"""
    #     return float(self.get_property(self.__section, 'DESIRE_PRESSURE_ANODE_ELECTROLYZER'))
    #
    # @property
    # def start_temperature_el(self) -> float:
    #     """Retruns start pressure of cathode of electrolyzer"""
    #     return float(self.get_property(self.__section, 'START_TEMPERATURE_ELECTROLYZER'))
    #
    # @property
    # def desire_temperature_el(self) -> float:
    #     """Retruns desired pressure of cathode of electrolyzer"""
    #     return float(self.get_property(self.__section, 'DESIRE_TEMPERATURE_ELECTROLYZER'))
    #
    # @property
    # def serial_scale(self) -> float:
    #     """Returns a linear scaling factor of cell in order to simulate a serial lithium_ion connection"""
    #     return float(self.get_property(self.__section, 'CELL_SERIAL_SCALE'))
    #
    # @property
    # def parallel_scale(self) -> float:
    #     """Returns a linear scaling factor of cell in order to simulate a parallel lithium_ion connection"""
    #     return float(self.get_property(self.__section, 'CELL_PARALLEL_SCALE'))
    #
    # @property
    # def cell_types(self) -> [str]:
    #     """Returns cell chemistry for simulation"""
    #     return self.get_property(self.__section, 'CELL_TYPE').replace(' ', '').split(',')
    #
    # @property
    # def serial_battery_connection(self) -> int:
    #     """Returns number of serial connected batteries"""
    #     return int(self.get_property(self.__section, 'SERIAL_CIRCUIT'))
    #
    # @property
    # def parallel_battery_connection(self) -> int:
    #     """Returns number of parallel connected batteries"""
    #     return int(self.get_property(self.__section, 'PARALLEL_CIRCUIT'))
    #
    # @property
    # def simulate_each_cell(self) -> bool:
    #     """Returns boolean value for multithreading of batteries"""
    #     return self.get_property(self.__section, 'SIMULATE_EACH_CELL') in ['True']
    #
    # @property
    # def thermal_model_el(self) -> str:
    #     """Returns name of thermal model """
    #     return self.get_property(self.__section, 'THERMAL_MODEL')
