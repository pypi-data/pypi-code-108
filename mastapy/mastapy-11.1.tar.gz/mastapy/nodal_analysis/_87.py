'''_87.py

VolumeElementShape
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_VOLUME_ELEMENT_SHAPE = python_net_import('SMT.MastaAPI.NodalAnalysis', 'VolumeElementShape')


__docformat__ = 'restructuredtext en'
__all__ = ('VolumeElementShape',)


class VolumeElementShape(Enum):
    '''VolumeElementShape

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _VOLUME_ELEMENT_SHAPE

    __hash__ = None

    TETRAHEDRAL = 0
    HEXAHEDRAL = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


VolumeElementShape.__setattr__ = __enum_setattr
VolumeElementShape.__delattr__ = __enum_delattr
