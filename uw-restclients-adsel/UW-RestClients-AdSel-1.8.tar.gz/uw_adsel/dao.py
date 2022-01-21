"""
Contains UW AdSEL DAO implementations.
"""
from restclients_core.dao import DAO
from os.path import abspath, dirname
import os


class ADSEL_DAO(DAO):
    def service_name(self):
        return 'adsel'

    def service_mock_paths(self):
        path = [abspath(os.path.join(dirname(__file__), "resources"))]
        return path
