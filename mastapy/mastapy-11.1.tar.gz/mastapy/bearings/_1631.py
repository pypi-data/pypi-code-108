'''_1631.py

BearingCageMaterial
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_BEARING_CAGE_MATERIAL = python_net_import('SMT.MastaAPI.Bearings', 'BearingCageMaterial')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingCageMaterial',)


class BearingCageMaterial(Enum):
    '''BearingCageMaterial

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _BEARING_CAGE_MATERIAL

    __hash__ = None

    STEEL = 0
    BRASS = 1
    PLASTIC = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


BearingCageMaterial.__setattr__ = __enum_setattr
BearingCageMaterial.__delattr__ = __enum_delattr
