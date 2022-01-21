"""
Loader for configuration files in json format
"""

import json

from ..exceptions import ConfigurationError
from .directory import ConfigurationFileDirectory
from .file import ConfigurationFile

JSON_FILE_EXTENSIONS = (
    '.json',
)


class JsonConfiguration(ConfigurationFile):
    """
    Configuration parser for JSON configuration files

    You can pass arguments to json.loads with loader_args
    """
    encoding = 'utf-8'

    def __init__(self, path=None, parent=None, debug_enabled=False, silent=False, **loader_args):
        self.__loader_args__ = loader_args
        super().__init__(path, parent=parent, debug_enabled=debug_enabled, silent=silent)

    def load(self, path):
        """
        Load specified JSON configuration file
        """
        path = self.__check_file_access__(path)
        try:
            self.parse_data(
                json.loads(path.open('r', encoding=self.encoding).read(), **self.__loader_args__)
            )
        except Exception as error:
            raise ConfigurationError(f'Error loading {path}: {error}') from error


class JsonConfigurationDirectory(ConfigurationFileDirectory):
    """
    Directory of JSON format configuration files
    """
    __file_loader_class__ = JsonConfiguration
    __extensions__ = JSON_FILE_EXTENSIONS
