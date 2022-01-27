from configparser import ConfigParser
from simses.commons.config.abstract_config import Config
from simses.commons.utils.utilities import get_path_for


class AnalysisConfig(Config):
    """
    All analysis configs are inherited from this class
    """

    CONFIG_NAME: str = 'analysis'
    CONFIG_PATH: str = get_path_for(CONFIG_NAME + Config.DEFAULTS)

    def __init__(self, path: str, config: ConfigParser):
        if path is None:
            path = self.CONFIG_PATH
        super().__init__(path, self.CONFIG_NAME, config)
