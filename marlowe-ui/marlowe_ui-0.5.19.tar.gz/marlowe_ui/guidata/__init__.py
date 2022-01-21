# define current data structure version
from .v1 import *  # noQA


def getversion(d):
    """get version number of datatype. if d['version'] is missing, 0 is returned"""
    return d.get('version', 0)
