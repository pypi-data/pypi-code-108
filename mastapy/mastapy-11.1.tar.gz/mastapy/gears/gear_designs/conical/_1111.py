'''_1111.py

FrontEndTypes
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_FRONT_END_TYPES = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Conical', 'FrontEndTypes')


__docformat__ = 'restructuredtext en'
__all__ = ('FrontEndTypes',)


class FrontEndTypes(Enum):
    '''FrontEndTypes

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _FRONT_END_TYPES

    __hash__ = None

    FLAT = 0
    CONICAL = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


FrontEndTypes.__setattr__ = __enum_setattr
FrontEndTypes.__delattr__ = __enum_delattr
