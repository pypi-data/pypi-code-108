from simses.commons.config.analysis.market import MarketProfileConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.profile.economic.market import MarketProfile
from simses.commons.profile.file import FileProfile
from simses.commons.timeseries.interpolation.last_value import LastValue


class FcrMarketProfile(MarketProfile):
    """
    Provides the FCR market prices
    """
    def __init__(self, general_config: GeneralSimulationConfig, config: MarketProfileConfig):
        super().__init__()
        self.__file: FileProfile = FileProfile(general_config, config.fcr_price_file, interpolation=LastValue())

    def next(self, time: float) -> float:
        return self.__file.next(time)

    def initialize_profile(self) -> None:
        return self.__file.initialize_file()

    def close(self):
        self.__file.close()
