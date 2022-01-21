'''_2243.py

HousedOrMounted
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_HOUSED_OR_MOUNTED = python_net_import('SMT.MastaAPI.SystemModel.PartModel.ImportFromCAD', 'HousedOrMounted')


__docformat__ = 'restructuredtext en'
__all__ = ('HousedOrMounted',)


class HousedOrMounted(Enum):
    '''HousedOrMounted

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _HOUSED_OR_MOUNTED

    __hash__ = None

    HOUSED = 0
    MOUNTED = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


HousedOrMounted.__setattr__ = __enum_setattr
HousedOrMounted.__delattr__ = __enum_delattr
