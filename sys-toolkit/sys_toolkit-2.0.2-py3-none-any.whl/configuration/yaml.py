"""
Loader for configuration files in yaml format
"""

import yaml

from ..exceptions import ConfigurationError
from .directory import ConfigurationFileDirectory
from .file import ConfigurationFile

YAML_FILE_EXTENSIONS = (
    '.yaml',
    '.yml',
)


class YamlConfiguration(ConfigurationFile):
    """
    Configuration parser for yaml configuration files
    """
    encoding = 'utf-8'

    def load(self, path):
        """
        Load specified YAML configuration file
        """
        path = self.__check_file_access__(path)

        try:
            self.parse_data(
                yaml.safe_load(path.open('r', encoding='utf-8'))
            )
        except Exception as error:
            raise ConfigurationError(f'Error loading {path}: {error}') from error


class YamlConfigurationDirectory(ConfigurationFileDirectory):
    """
    Directory of yaml format configuration files
    """
    __file_loader_class__ = YamlConfiguration
    __extensions__ = YAML_FILE_EXTENSIONS
