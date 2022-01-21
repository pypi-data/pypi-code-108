'''_1002.py

GearFitSystems
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_GEAR_FIT_SYSTEMS = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'GearFitSystems')


__docformat__ = 'restructuredtext en'
__all__ = ('GearFitSystems',)


class GearFitSystems(Enum):
    '''GearFitSystems

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _GEAR_FIT_SYSTEMS

    __hash__ = None

    NONE = 0
    DIN_39671978 = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


GearFitSystems.__setattr__ = __enum_setattr
GearFitSystems.__delattr__ = __enum_delattr
