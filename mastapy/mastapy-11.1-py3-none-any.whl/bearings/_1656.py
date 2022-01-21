'''_1656.py

TiltingPadTypes
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_TILTING_PAD_TYPES = python_net_import('SMT.MastaAPI.Bearings', 'TiltingPadTypes')


__docformat__ = 'restructuredtext en'
__all__ = ('TiltingPadTypes',)


class TiltingPadTypes(Enum):
    '''TiltingPadTypes

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _TILTING_PAD_TYPES

    __hash__ = None

    NONEQUALISED = 0
    EQUALISED = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


TiltingPadTypes.__setattr__ = __enum_setattr
TiltingPadTypes.__delattr__ = __enum_delattr
