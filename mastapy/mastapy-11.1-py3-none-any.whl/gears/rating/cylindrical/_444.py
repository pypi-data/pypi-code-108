'''_444.py

ScuffingMethods
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_SCUFFING_METHODS = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical', 'ScuffingMethods')


__docformat__ = 'restructuredtext en'
__all__ = ('ScuffingMethods',)


class ScuffingMethods(Enum):
    '''ScuffingMethods

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _SCUFFING_METHODS

    __hash__ = None

    AGMA_2001B88_OLD = 0
    AGMA_925A03_NEW = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ScuffingMethods.__setattr__ = __enum_setattr
ScuffingMethods.__delattr__ = __enum_delattr
