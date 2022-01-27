import os
import pathlib
from abc import ABC
from configparser import ConfigParser
from simses.commons.utils.utilities import convert_path_codec
from simses.data import DATA_DIR


class Config(ABC):
    """
    The Config class contains all necessary configuration options of a package, e.g. simulation or analysis. In addition,
    the Config class selects proper options from defaults, local or in code configurations. For all sections of each
    config a own config class is provided and is inherited from Config.

    Configs are taken from INI files in config package. *.defaults.ini are read in first, followed by *.local.ini and
    finally overwritten by a ConfigParser passed in as a constructor argument. This threefold delivers functionality by
    default if you just want to run a possible setup. If a specific simulation should be run locally, the config parameters
    of the *.local.ini file will overwrite the configuration of defaults; only necessary parameters can be included in
    the local config file. Furthermore, for sensitivity analysis the ConfigParser argument is taken into account to
    automate various configurations. The ConfigParser should have the same structure as the config files and overwrites
    the given values.
    """

    CONFIG_EXT: str = '.ini'
    DEFAULTS: str = '.defaults' + CONFIG_EXT
    LOCAL: str = '.local' + CONFIG_EXT

    __used_config: dict = dict()
    __extensions: [str] = [DEFAULTS, LOCAL, CONFIG_EXT]

    def __init__(self, path: str, name: str, config: ConfigParser):
        """
        Constructor of Config

        Parameters
        ----------
        path :
            path to config file folder
        name :
            name of config file
        config :
            ConfigParser overwriting values from config file
        """
        # if path is None:
        #     path = get_path_for(name + self.DEFAULTS)
        self.__config: ConfigParser = ConfigParser()
        for extension in self.__extensions:
            self.__config.read(path + name + extension)
        self.__file_name: str = name + self.CONFIG_EXT
        self.__overwrite_config_with(config)

    def get_property(self, section: str, option: str):
        """
        Returns the value for given section and option

        Parameters
        ----------
        section :
            section of config
        option :
            option of config

        Returns
        -------

        """
        value = None
        try:
            value = self.__config[section][option]
            self.__add_to_used_config(section, option, value)
        except KeyError as err:
            raise err
        finally:
            return value

    def __overwrite_config_with(self, config: ConfigParser):
        if config is not None:
            for section in config.sections():
                if section in self.__config.sections():
                    for option in config.options(section):
                        if option in self.__config.options(section):
                            value = config[section][option]
                            # print('[' + type(self).__name__ + '] Setting new value in section ' + section +
                            #       ' for option ' + option + ' with ' + value)
                            self.__config[section][option] = value

    def __add_to_used_config(self, section: str, option: str, value: str):
        key: str = self.__file_name
        if key not in self.__used_config.keys():
            self.__used_config[key] = ConfigParser()
        config: ConfigParser = self.__used_config[key]
        if section not in config.sections():
            config.add_section(section)
        if option not in config.options(section):
            config.set(section, option, value)

    def write_config_to(self, path: str) -> None:
        """
        Write current config to a file in given path

        Parameters
        ----------
        path :
            directory in which config file should be written

        Returns
        -------

        """
        # TODO how to write only used configs?
        # used_config: ConfigParser = self.__used_config[self.__file_name]
        with open(path + self.__file_name, 'w') as configfile:
            self.__config.write(configfile)
            # used_config.write(configfile)

    def get_data_path(self, path) -> str:
        path = convert_path_codec(path)
        if os.path.isabs(path):
            return pathlib.Path(path).as_posix() + '/'
        return DATA_DIR + path
