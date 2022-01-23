#
# Python Utils
#
# Author: Carles Mateo
# Creation Date: 2014-11-11 18:18 Barcelona
# Last Update: 2021-04-10 11:15 Ireland
# Description: Class to deal with Python functionalities and compatibility
#


import sys


class PythonUtils:

    def get_python_version(self):
        """
        Returns the version of Python

        Examples:
        sys.version_info(major=2, minor=7, micro=18, releaselevel='final', serial=0)
        sys.version_info(major=3, minor=8, micro=5, releaselevel='final', serial=0)
        :return: s_version, i_major, i_minor, i_micro, s_releaselevel
        """

        # This only works with Python3, so changing to compatible Python2 and Python3
        # i_major = sys.version_info["major"]
        # i_minor = sys.version_info["minor"]
        # i_micro = sys.version_info["micro"]

        i_major = sys.version_info[0]
        i_minor = sys.version_info[1]
        i_micro = sys.version_info[2]

        s_releaselevel = sys.version_info[3]

        s_version = str(i_major) + "." + str(i_minor) + "." + str(i_micro)

        return s_version, i_major, i_minor, i_micro, s_releaselevel

    def is_python_2(self):
        s_version, i_major, i_minor, i_micro, s_releaselevel = self.get_python_version()

        if i_major == 2:
            return True

        return False

    def is_python_3(self):
        s_version, i_major, i_minor, i_micro, s_releaselevel = self.get_python_version()

        if i_major == 3:
            return True

        return False
