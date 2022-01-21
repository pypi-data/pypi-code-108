'''_1108.py

CutterBladeType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CUTTER_BLADE_TYPE = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Conical', 'CutterBladeType')


__docformat__ = 'restructuredtext en'
__all__ = ('CutterBladeType',)


class CutterBladeType(Enum):
    '''CutterBladeType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CUTTER_BLADE_TYPE

    __hash__ = None

    STRAIGHT = 0
    CIRCULAR_ARC = 1
    PARABOLIC = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


CutterBladeType.__setattr__ = __enum_setattr
CutterBladeType.__delattr__ = __enum_delattr
