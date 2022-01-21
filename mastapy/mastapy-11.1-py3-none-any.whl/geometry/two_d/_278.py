'''_278.py

InternalExternalType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_INTERNAL_EXTERNAL_TYPE = python_net_import('SMT.MastaAPI.Geometry.TwoD', 'InternalExternalType')


__docformat__ = 'restructuredtext en'
__all__ = ('InternalExternalType',)


class InternalExternalType(Enum):
    '''InternalExternalType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _INTERNAL_EXTERNAL_TYPE

    __hash__ = None

    INTERNAL = 0
    EXTERNAL = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


InternalExternalType.__setattr__ = __enum_setattr
InternalExternalType.__delattr__ = __enum_delattr
