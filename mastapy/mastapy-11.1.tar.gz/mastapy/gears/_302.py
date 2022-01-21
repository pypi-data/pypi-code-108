'''_302.py

MicroGeometryInputTypes
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_MICRO_GEOMETRY_INPUT_TYPES = python_net_import('SMT.MastaAPI.Gears', 'MicroGeometryInputTypes')


__docformat__ = 'restructuredtext en'
__all__ = ('MicroGeometryInputTypes',)


class MicroGeometryInputTypes(Enum):
    '''MicroGeometryInputTypes

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _MICRO_GEOMETRY_INPUT_TYPES

    __hash__ = None

    FACTORS = 0
    MEASUREMENTS = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


MicroGeometryInputTypes.__setattr__ = __enum_setattr
MicroGeometryInputTypes.__delattr__ = __enum_delattr
