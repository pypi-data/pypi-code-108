'''_1299.py

CoordinateSystemForRotation
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_COORDINATE_SYSTEM_FOR_ROTATION = python_net_import('SMT.MastaAPI.MathUtility', 'CoordinateSystemForRotation')


__docformat__ = 'restructuredtext en'
__all__ = ('CoordinateSystemForRotation',)


class CoordinateSystemForRotation(Enum):
    '''CoordinateSystemForRotation

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _COORDINATE_SYSTEM_FOR_ROTATION

    __hash__ = None

    WORLD_COORDINATE_SYSTEM = 0
    LOCAL_COORDINATE_SYSTEM = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


CoordinateSystemForRotation.__setattr__ = __enum_setattr
CoordinateSystemForRotation.__delattr__ = __enum_delattr
