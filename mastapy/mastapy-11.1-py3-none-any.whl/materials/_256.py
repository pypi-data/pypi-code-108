'''_256.py

VDI2736LubricantType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_VDI2736_LUBRICANT_TYPE = python_net_import('SMT.MastaAPI.Materials', 'VDI2736LubricantType')


__docformat__ = 'restructuredtext en'
__all__ = ('VDI2736LubricantType',)


class VDI2736LubricantType(Enum):
    '''VDI2736LubricantType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _VDI2736_LUBRICANT_TYPE

    __hash__ = None

    OIL = 0
    GREASE = 1
    WATEROIL_EMULSION = 2
    OIL_MIST = 3
    NONE_DRY_RUNNING = 4


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


VDI2736LubricantType.__setattr__ = __enum_setattr
VDI2736LubricantType.__delattr__ = __enum_delattr
