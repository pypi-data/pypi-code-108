'''_1258.py

DirectionOfMeasuredModifications
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_DIRECTION_OF_MEASURED_MODIFICATIONS = python_net_import('SMT.MastaAPI.Cycloidal', 'DirectionOfMeasuredModifications')


__docformat__ = 'restructuredtext en'
__all__ = ('DirectionOfMeasuredModifications',)


class DirectionOfMeasuredModifications(Enum):
    '''DirectionOfMeasuredModifications

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _DIRECTION_OF_MEASURED_MODIFICATIONS

    __hash__ = None

    NORMAL = 0
    RADIAL = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


DirectionOfMeasuredModifications.__setattr__ = __enum_setattr
DirectionOfMeasuredModifications.__delattr__ = __enum_delattr
