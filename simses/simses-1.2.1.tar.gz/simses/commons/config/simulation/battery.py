from configparser import ConfigParser

from simses.commons.config.simulation.simulation_config import SimulationConfig


class BatteryConfig(SimulationConfig):
    """
    Battery specific configs
    """

    SECTION: str = 'BATTERY'
    START_SOC: str = 'START_SOC'
    MIN_SOC: str = 'MIN_SOC'
    MAX_SOC: str = 'MAX_SOC'
    EOL:str = 'EOL'
    START_SOH: str = 'START_SOH'
    START_SOH_SHARE: str = 'START_SOH_SHARE'
    EXACT_SIZE: str = 'EXACT_SIZE'
    CELL_SERIAL_SCALE: str = 'CELL_SERIAL_SCALE'
    CELL_PARALLEL_SCALE: str = 'CELL_PARALLEL_SCALE'
    DEGRADATION_MODEL_NUMBER: str = 'DEGRADATION_MODEL_NUMBER'
    CONSIDER_VOLTAGE_LIMIT: str = 'CONSIDER_VOLTAGE_LIMIT'
    MULTI_MODEL_PARAMETERS: str = 'MULTI_MODEL_PARAMETERS'
    CALENDAR_LIFETIME: str = 'CALENDAR_LIFETIME'
    CYCLE_LIFETIME: str = 'CYCLE_LIFETIME'

    def __init__(self, config: ConfigParser, path: str = None):
        super().__init__(path, config)

    @property
    def soc(self) -> float:
        """
        Minimum SOC (0-1)

        Returns
        -------
        float:
            Returns the start soc from data_config file

        """
        return float(self.get_property(self.SECTION, self.START_SOC))

    @property
    def min_soc(self) -> float:
        """
        Minimum SOC (0-1)

        Returns
        -------
        float:
            Returns the minimum soc from data_config file

        """
        return float(self.get_property(self.SECTION, self.MIN_SOC))

    @property
    def max_soc(self) -> float:
        """
        Maximum SOC (0-1)

        Returns
        -------
        float:
            Returns the maximum soc from data_config file

        """
        return float(self.get_property(self.SECTION, self.MAX_SOC))

    @property
    def eol(self) -> float:
        """
        End of Life criteria (0-1)

        Returns
        -------
        float:
            Returns EOL criteria in % from data_config file

        """
        return float(self.get_property(self.SECTION, self.EOL))

    @property
    def start_soh(self) -> float:
        """
        End of Life criteria (0-1)

        Returns
        -------
        float:
            Returns start SOH from data_config file

        """
        return float(self.get_property(self.SECTION, self.START_SOH))

    @property
    def exact_size(self) -> bool:
        """Returns selection for exact sizing True/False"""
        return self.get_property(self.SECTION, self.EXACT_SIZE) in ['True']

    @property
    def start_soh_share(self) -> float:
        """
        Share of start SOH between calendar and cyclic degradation for both, capacity decrease and resistance increase

        Returns
        -------
        float:
            Returns start SOH share in p.u.

        """
        return float(self.get_property(self.SECTION, self.START_SOH_SHARE))

    @property
    def degradation_model_number(self) -> int:
        """
        Number / identifier for selected degradation model for degradation models that read parameters from CSV files
        (e.g. SonyLFP).

        Returns
        -------
        int:
            Returns the degradation model parameter number that is to be read from the CSV.
            Returns 1 if not specified in config.

        """
        try:
            return int(self.get_property(self.SECTION, self.DEGRADATION_MODEL_NUMBER))
        except (KeyError, TypeError):
            return 1

    @property
    def multi_model_parameters(self) -> str:
        """
        Parameters for multi model degradation models. Under development.

        Returns
        -------
        str:
            Comma seperated parameters in no particular order

        """
        return str(self.get_property(self.SECTION, self.MULTI_MODEL_PARAMETERS))

    @property
    def serial_scale(self) -> float:
        """Returns a linear scaling factor of cell in order to simulate a serial lithium_ion connection"""
        return float(self.get_property(self.SECTION, self.CELL_SERIAL_SCALE))

    @property
    def parallel_scale(self) -> float:
        """Returns a linear scaling factor of cell in order to simulate a parallel lithium_ion connection"""
        return float(self.get_property(self.SECTION, self.CELL_PARALLEL_SCALE))

    @property
    def max_equivalent_full_cycles(self) -> float:
        """Returns a number of maximum equivalent full cycles for GenericCell degradation"""
        try:
            return float(self.get_property(self.SECTION, self.CYCLE_LIFETIME))
        except TypeError:
            return 2000.0

    @property
    def max_calendar_lifetime(self) -> float:
        """Returns a maximum calendar lifetime for GenericCell degradation in years"""
        try:
            return float(self.get_property(self.SECTION, self.CALENDAR_LIFETIME))
        except TypeError:
            return 5.

    @property
    def consider_voltage_limit(self) -> bool:
        """Returns if current should be limited by charge / discharge end voltage, default: True"""
        try:
            return self.get_property(self.SECTION, self.CONSIDER_VOLTAGE_LIMIT) in ['True', None]
        except (KeyError, TypeError):
            return True
