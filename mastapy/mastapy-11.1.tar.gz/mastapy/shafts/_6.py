'''_6.py

AGMAHardeningType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_AGMA_HARDENING_TYPE = python_net_import('SMT.MastaAPI.Shafts', 'AGMAHardeningType')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAHardeningType',)


class AGMAHardeningType(Enum):
    '''AGMAHardeningType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _AGMA_HARDENING_TYPE

    __hash__ = None

    DUCTILE_THROUGH_HARDENED_STEEL = 0
    SURFACE_HARDENED_STEEL = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


AGMAHardeningType.__setattr__ = __enum_setattr
AGMAHardeningType.__delattr__ = __enum_delattr
