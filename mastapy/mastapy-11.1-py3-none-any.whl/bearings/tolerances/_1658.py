'''_1658.py

InternalClearanceClass
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_INTERNAL_CLEARANCE_CLASS = python_net_import('SMT.MastaAPI.Bearings.Tolerances', 'InternalClearanceClass')


__docformat__ = 'restructuredtext en'
__all__ = ('InternalClearanceClass',)


class InternalClearanceClass(Enum):
    '''InternalClearanceClass

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _INTERNAL_CLEARANCE_CLASS

    __hash__ = None

    GROUP_2 = 0
    GROUP_N = 1
    GROUP_3 = 2
    GROUP_4 = 3
    GROUP_5 = 4


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


InternalClearanceClass.__setattr__ = __enum_setattr
InternalClearanceClass.__delattr__ = __enum_delattr
