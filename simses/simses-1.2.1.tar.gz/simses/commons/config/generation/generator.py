import json
import pickle
from configparser import ConfigParser


class ConfigGenerator:

    def __init__(self):
        self.__config: ConfigParser = ConfigParser()

    def load_config_from(self, file: str) -> None:
        """
        Loads config from given file

        Parameters
        ----------
        file :
            path to config file

        Returns
        -------

        """
        self.__config.read(file)

    def get_config(self) -> ConfigParser:
        """

        Returns
        -------
        ConfigParser:
            copy of config setup to be passed to SimSES
        """
        rep = pickle.dumps(self.__config)
        new_config = pickle.loads(rep)
        return new_config

    def show(self) -> None:
        """
        Printing config setup

        Returns
        -------

        """
        config: dict = {section: dict(self.__config[section]) for section in self.__config.sections()}
        print(json.dumps(config, sort_keys=True, indent=4))

    def _set(self, section: str, option: str, value: str) -> None:
        if value is None:
            return
        config: ConfigParser = self.__config
        if section not in config.sections():
            config.add_section(section)
        config.set(section, option, value)

    def _set_bool(self, section: str, option: str, value: bool) -> None:
        self._set(section, option, 'True' if value else 'False')

    def _clear(self, section: str, option: str) -> None:
        self._set(section, option, '')

    def _get(self, section: str, option: str) -> str:
        try:
            return self.__config[section][option]
        except KeyError as err:
            raise err

    def _add(self, section: str, option: str, value: str) -> None:
        prop: str = self._get(section, option)
        prop += '\n' + value
        self._set(section, option, prop)

    def _get_id_from(self, section: str, option: str, delimiter: str = '\n') -> str:
        try:
            prop: str = self._get(section, option)
            return '_' + str(len(prop.split(delimiter)))
        except KeyError:
            return '_' + str(0)
