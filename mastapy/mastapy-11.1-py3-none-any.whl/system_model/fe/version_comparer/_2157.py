'''_2157.py

LoadCasesToRun
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_LOAD_CASES_TO_RUN = python_net_import('SMT.MastaAPI.SystemModel.FE.VersionComparer', 'LoadCasesToRun')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadCasesToRun',)


class LoadCasesToRun(Enum):
    '''LoadCasesToRun

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _LOAD_CASES_TO_RUN

    __hash__ = None

    HIGHEST_LOAD_IN_EACH_DESIGN_STATE = 0
    HIGHEST_LOAD = 1
    ALL = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


LoadCasesToRun.__setattr__ = __enum_setattr
LoadCasesToRun.__delattr__ = __enum_delattr
