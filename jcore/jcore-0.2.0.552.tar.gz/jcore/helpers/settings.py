import jcore.exceptions
import json
import pathlib
import yaml



class Settings():
    """A helper class to collect and retrieve settings"""
    __settingsData: dict
    
    def __init__(self, path=None):
        if path is None:
            path = "config.yaml"
        if not pathlib.Path(path).exists():
            path = "./config.yaml"
        if not pathlib.Path(path).exists():
            path = "./bots/config.yaml"
        if not pathlib.Path(path).exists():
            path = "./Common/config.yaml"
        if not pathlib.Path(path).exists():
            path = "../Common/config.yaml"
        if not pathlib.Path(path).exists():
            path = "../../Common/config.yaml"
        if path is None:
            path = "config.json"
        if not pathlib.Path(path).exists():
            path = "./config.json"
        if not pathlib.Path(path).exists():
            path = "./bots/config.json"
        if not pathlib.Path(path).exists():
            path = "./Common/config.json"
        if not pathlib.Path(path).exists():
            path = "../Common/config.json"
        if not pathlib.Path(path).exists():
            path = "../../Common/config.json"
        if not pathlib.Path(path).exists():
            raise jcore.exceptions.ConfigFileNotFound("Config file could not be found.")
        self.__settingsData = self.__parse_file(path)
        self.path = path
    
    def get_setting(self, key:str) -> str:
        """Attempt to retrieve a setting from the settings store.

        Parameters
        ----------
        key : str
            The settings key you want to retrieve.

        Returns
        -------
        str
            The value of the setting for the key requested

        Raises
        ------
        jcore.exceptions.MissingSetting
            If the key requested is not in the list of settings.
        """
        try:
            setting = self.__fetchSetting(key, self.__settingsData)
        except KeyError:
            raise jcore.exceptions.MissingSetting(f"Key: '{key}' was not found in the config file '{self.path}'")
        if setting is None:
            raise jcore.exceptions.MissingSetting(f"Key: '{key}' was not found in the config file '{self.path}'")
        return self.__fetchSetting(key, self.__settingsData)


    def has_key(self, key:str) -> bool:
        """Check if a setting exists in the settings store.

        Parameters
        ----------
        key : str
            The settings key you want to retrieve.

        Returns
        -------
        bool
            `True`: the setting exists.
            `False`: the setting does not exist.

        Raises
        ------
        jcore.exceptions.MissingSetting
            If the key requested is not in the list of settings.
        """
        try:
            self.get_setting(key)
            return True
        except jcore.exceptions.MissingSetting:
            return False
    
    def __fetchSetting(self, key:str, sublist:dict):
        keynest = key.split(".", 1)
        if len(keynest) == 1:
            try:
                return sublist[keynest[0]]
            except:
                return None
        return self.__fetchSetting(keynest[1], sublist[keynest[0]])
        
    def __parse_file(self, path):
        data = None
        with open(pathlib.Path(path), 'r') as stream:
            if path.endswith(".yaml"):
                data = yaml.safe_load(stream)
            elif path.endswith(".json"):
                data = json.load(stream)
            else:
                raise jcore.exceptions.ConfigFileNotFound("Config file must be a .yaml or a .json file")
        return data
    
    def get_all_settings(self) -> dict:
        """Return the current settings store.

        Returns
        -------
        dict
            Return the settings store
        """
        return self.__settingsData

    def __repr__(self):
        return f"[Settings]: Loaded {len(self.__settingsData)} settings from file: '{self.path}'"