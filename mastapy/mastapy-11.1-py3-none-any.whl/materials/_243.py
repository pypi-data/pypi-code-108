'''_243.py

MetalPlasticType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_METAL_PLASTIC_TYPE = python_net_import('SMT.MastaAPI.Materials', 'MetalPlasticType')


__docformat__ = 'restructuredtext en'
__all__ = ('MetalPlasticType',)


class MetalPlasticType(Enum):
    '''MetalPlasticType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _METAL_PLASTIC_TYPE

    __hash__ = None

    PLASTIC = 0
    METAL = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


MetalPlasticType.__setattr__ = __enum_setattr
MetalPlasticType.__delattr__ = __enum_delattr
