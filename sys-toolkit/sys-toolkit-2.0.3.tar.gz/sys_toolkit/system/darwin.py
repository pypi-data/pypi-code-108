"""
System information lookup functions specific to MacOS Darwin
"""

from inflection import underscore

from ..subprocess import run_command_lineoutput


class SoftwareVersion:
    """
    Parse MacOS 'sw_vers' command output to get MacOS version details
    """
    __data__ = {}

    def __repr__(self):
        return f'{self.product_name} {self.product_version} {self.build_version}'

    @staticmethod
    def __get_sw_vers_data__():
        """
        Run sw_vers and output it's data
        """
        stdout, _stderr = run_command_lineoutput('sw_vers')
        data = {}
        for line in stdout:
            key, value = [field.strip() for field in line.split(':')]
            data[underscore(key)] = value
        return data

    @property
    def product_name(self):
        """
        Return MacOS product name
        """
        if not self.__data__:
            self.__data__ = self.__get_sw_vers_data__()
        return self.__data__['product_name']

    @property
    def product_version(self):
        """
        Return MacOS product version
        """
        if not self.__data__:
            self.__data__ = self.__get_sw_vers_data__()
        return self.__data__['product_version']

    @property
    def build_version(self):
        """
        Return MacOS build version
        """
        if not self.__data__:
            self.__data__ = self.__get_sw_vers_data__()
        return self.__data__['build_version']
