'''_178.py

DegreeOfFreedomType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_DEGREE_OF_FREEDOM_TYPE = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses.FullFEReporting', 'DegreeOfFreedomType')


__docformat__ = 'restructuredtext en'
__all__ = ('DegreeOfFreedomType',)


class DegreeOfFreedomType(Enum):
    '''DegreeOfFreedomType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _DEGREE_OF_FREEDOM_TYPE

    __hash__ = None

    INDEPENDENT = 0
    DEPENDENT = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


DegreeOfFreedomType.__setattr__ = __enum_setattr
DegreeOfFreedomType.__delattr__ = __enum_delattr
