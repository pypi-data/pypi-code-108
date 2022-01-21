'''_1661.py

FitType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_FIT_TYPE = python_net_import('SMT.MastaAPI.Bearings.Tolerances', 'FitType')


__docformat__ = 'restructuredtext en'
__all__ = ('FitType',)


class FitType(Enum):
    '''FitType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _FIT_TYPE

    __hash__ = None

    INTERFERENCE = 0
    TRANSITION = 1
    CLEARANCE = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


FitType.__setattr__ = __enum_setattr
FitType.__delattr__ = __enum_delattr
