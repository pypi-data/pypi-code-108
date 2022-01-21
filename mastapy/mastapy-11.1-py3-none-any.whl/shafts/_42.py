'''_42.py

SurfaceFinishes
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_SURFACE_FINISHES = python_net_import('SMT.MastaAPI.Shafts', 'SurfaceFinishes')


__docformat__ = 'restructuredtext en'
__all__ = ('SurfaceFinishes',)


class SurfaceFinishes(Enum):
    '''SurfaceFinishes

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _SURFACE_FINISHES

    __hash__ = None

    HIGHLY_POLISHED_NOMINAL = 0
    POLISHED = 1
    GROUND = 2
    COLD_DRAWN_OR_MACHINED_63µIN_16µM = 3
    COLD_DRAWN_OR_MACHINED_125µIN_32µM = 4
    COLD_DRAWN_OR_MACHINED_250µIN_63µM = 5
    COLD_DRAWN_OR_MACHINED_500µIN_125µM = 6
    HOT_ROLLED = 7
    FORGED = 8
    USERSPECIFIED = 9


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


SurfaceFinishes.__setattr__ = __enum_setattr
SurfaceFinishes.__delattr__ = __enum_delattr
