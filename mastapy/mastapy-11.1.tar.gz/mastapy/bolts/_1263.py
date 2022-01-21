'''_1263.py

AxialLoadType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_AXIAL_LOAD_TYPE = python_net_import('SMT.MastaAPI.Bolts', 'AxialLoadType')


__docformat__ = 'restructuredtext en'
__all__ = ('AxialLoadType',)


class AxialLoadType(Enum):
    '''AxialLoadType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _AXIAL_LOAD_TYPE

    __hash__ = None

    DYNAMIC_AND_ECCENTRIC = 0
    DYNAMIC_AND_CONCENTRIC = 1
    STATIC_AND_ECCENTRIC = 2
    STATIC_AND_CONCENTRIC = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


AxialLoadType.__setattr__ = __enum_setattr
AxialLoadType.__delattr__ = __enum_delattr
