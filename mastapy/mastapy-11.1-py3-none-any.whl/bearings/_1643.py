'''_1643.py

JournalBearingType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_JOURNAL_BEARING_TYPE = python_net_import('SMT.MastaAPI.Bearings', 'JournalBearingType')


__docformat__ = 'restructuredtext en'
__all__ = ('JournalBearingType',)


class JournalBearingType(Enum):
    '''JournalBearingType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _JOURNAL_BEARING_TYPE

    __hash__ = None

    PLAIN_OIL_FED = 0
    PLAIN_GREASE_FILLED = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


JournalBearingType.__setattr__ = __enum_setattr
JournalBearingType.__delattr__ = __enum_delattr
