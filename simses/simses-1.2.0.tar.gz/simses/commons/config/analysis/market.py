from configparser import ConfigParser
from simses.commons.config.analysis.analysis_config import AnalysisConfig


class MarketProfileConfig(AnalysisConfig):

    """
    Market profile configs
    """

    SECTION: str = 'MARKET_PROFILE'

    def __init__(self, config: ConfigParser, path: str = None):
        super().__init__(path, config)
        # self.__log: Logger = Logger(type(self).__name__)

    @property
    def market_profile_dir(self) -> str:
        """Returns directory of market profiles from __analysis_config file_name"""
        return self.get_data_path(self.get_property(self.SECTION, 'MARKET_PROFILE_DIR'))

    @property
    def fcr_price_file(self) -> str:
        """Returns soc profile file_name name from __analysis_config file_name"""
        return self.market_profile_dir + self.get_property(self.SECTION, 'FCR_PRICE_PROFILE')

    @property
    def intraday_price_file(self) -> str:
        """ Return PV generation profile file_name name from __analysis_config file_name"""
        return self.market_profile_dir + self.get_property(self.SECTION, 'INTRADAY_PRICE_PROFILE')

