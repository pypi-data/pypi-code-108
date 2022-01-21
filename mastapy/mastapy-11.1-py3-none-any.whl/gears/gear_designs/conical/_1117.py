'''_1117.py

TopremEntryType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_TOPREM_ENTRY_TYPE = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Conical', 'TopremEntryType')


__docformat__ = 'restructuredtext en'
__all__ = ('TopremEntryType',)


class TopremEntryType(Enum):
    '''TopremEntryType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _TOPREM_ENTRY_TYPE

    __hash__ = None

    TOPREM_LETTER = 0
    VALUES = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


TopremEntryType.__setattr__ = __enum_setattr
TopremEntryType.__delattr__ = __enum_delattr
