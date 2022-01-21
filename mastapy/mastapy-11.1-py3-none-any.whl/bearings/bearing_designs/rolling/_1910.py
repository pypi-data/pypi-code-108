'''_1910.py

RollerEndShape
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ROLLER_END_SHAPE = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling', 'RollerEndShape')


__docformat__ = 'restructuredtext en'
__all__ = ('RollerEndShape',)


class RollerEndShape(Enum):
    '''RollerEndShape

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ROLLER_END_SHAPE

    __hash__ = None

    FLAT = 0
    DOMED = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


RollerEndShape.__setattr__ = __enum_setattr
RollerEndShape.__delattr__ = __enum_delattr
