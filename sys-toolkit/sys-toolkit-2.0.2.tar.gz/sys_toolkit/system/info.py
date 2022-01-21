"""
Information for local system
"""

from ..platform import detect_platform_family, detect_toolchain_family
from ..subprocess import run_command_lineoutput


class SystemInfo:
    """
    Container for system information details
    """
    __platform_fomily__ = None
    __toolchain_family__ = None
    __hostname__ = None

    def __get_hostname__(self):
        """
        Get hostname using platform toolchain specific command line command
        """
        if self.toolchain_family in ('bsd', 'gnu'):
            stdout, _stderr = run_command_lineoutput('hostname', '-s')
            if not stdout:
                raise ValueError('Error running command "hostname -s"')
            return stdout[0]
        return None

    @property
    def platform_family(self):
        """
        Return hostname
        """
        if self.__platform_fomily__ is None:
            self.__platform_fomily__ = detect_platform_family()
        return self.__platform_fomily__

    @property
    def toolchain_family(self):
        """
        Return hostname
        """
        if self.__toolchain_family__ is None:
            self.__toolchain_family__ = detect_toolchain_family()
        return self.__toolchain_family__

    @property
    def hostname(self):
        """
        Return hostname
        """
        if self.__hostname__ is None:
            self.__hostname__ = self.__get_hostname__()
        return self.__hostname__
