from configparser import ConfigParser
from datetime import datetime

from pytz import timezone

from simses.commons.config.simulation.simulation_config import SimulationConfig


class GeneralSimulationConfig(SimulationConfig):
    """
    General simulation configs
    """

    SECTION: str = 'GENERAL'

    START: str = 'START'
    END: str = 'END'
    TIME_FORMAT: str = '%Y-%m-%d %H:%M:%S'
    TIME_STEP: str = 'TIME_STEP'
    EXPORT_DATA: str = 'EXPORT_DATA'
    LOOP: str = 'LOOP'
    EXPORT_INTERVAL: str = 'EXPORT_INTERVAL'

    __UTC: timezone = timezone('UTC')

    def __init__(self, config: ConfigParser, path: str = None):
        super().__init__(path, config)

    @property
    def timestep(self) -> float:
        """Returns simulation timestep in s"""
        return float(self.get_property(self.SECTION, self.TIME_STEP))

    @property
    def start(self) -> float:
        """Returns simulation start timestamp"""
        date: str = self.get_property(self.SECTION, self.START)
        return self.__extract_utc_timestamp_from(date)

    @property
    def end(self) -> float:
        """Returns simulation end timestamp"""
        date: str = self.get_property(self.SECTION, self.END)
        return self.__extract_utc_timestamp_from(date)

    def __extract_utc_timestamp_from(self, date: str) -> float:
        date: datetime = datetime.strptime(date, self.TIME_FORMAT)
        return self.__UTC.localize(date).timestamp()

    @property
    def duration(self) -> float:
        """Returns simulation duration in s from __analysis_config file_name"""
        return self.end - self.start

    @property
    def loop(self) -> int:
        """Returns number of simulation loops"""
        return int(self.get_property(self.SECTION, self.LOOP))

    @property
    def export_interval(self) -> float:
        """Returns interval to write value to file"""
        return float(self.get_property(self.SECTION, self.EXPORT_INTERVAL))

    @property
    def export_data(self) -> bool:
        """Returns selection for data export True/False"""
        return self.get_property(self.SECTION, self.EXPORT_DATA) in ['True']
