import configparser
import os
import sys


class Setting(object):
    """
    公共

    """
    def __init__(self, config_path: str):
        # self.config_path = os.path.dirname(__file__)
        self.config_path = config_path
        self.cfg = configparser.ConfigParser()
        if sys.platform == "darwin":
            config_path = config_path.replace('\\', '/')
        if sys.platform == "win32":
            config_path = config_path.replace('/', '\\')
        self.cfg.read(config_path, encoding='utf-8')

    def get_setting(self, section, my_setting):
        """
        section:
        my_setting
        """
        try:
            ret = self.cfg.get(section, my_setting)
            return ret
        except Exception as e:
            print(e)

    def get_int(self, section, my_setting):
        """
        section:
        my_setting
        """
        try:
            ret = self.cfg.getint(section, my_setting)
            return int(ret)
        except Exception as e:
            raise e

    def set_data(self, section, my_setting, data):
        """
        修改config
        """
        self.cfg.set(section, my_setting, data)
