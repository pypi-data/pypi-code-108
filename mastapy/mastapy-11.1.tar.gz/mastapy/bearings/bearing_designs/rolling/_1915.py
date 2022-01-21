'''_1915.py

SleeveType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_SLEEVE_TYPE = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling', 'SleeveType')


__docformat__ = 'restructuredtext en'
__all__ = ('SleeveType',)


class SleeveType(Enum):
    '''SleeveType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _SLEEVE_TYPE

    __hash__ = None

    NONE = 0
    WITHDRAWAL = 1
    ADAPTER = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


SleeveType.__setattr__ = __enum_setattr
SleeveType.__delattr__ = __enum_delattr
