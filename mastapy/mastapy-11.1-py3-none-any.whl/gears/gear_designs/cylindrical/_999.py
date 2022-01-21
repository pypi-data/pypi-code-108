'''_999.py

DoubleAxisScaleAndRange
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_DOUBLE_AXIS_SCALE_AND_RANGE = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'DoubleAxisScaleAndRange')


__docformat__ = 'restructuredtext en'
__all__ = ('DoubleAxisScaleAndRange',)


class DoubleAxisScaleAndRange(Enum):
    '''DoubleAxisScaleAndRange

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _DOUBLE_AXIS_SCALE_AND_RANGE

    __hash__ = None

    MASTA_DEFAULT = 0
    EQUAL_SCALE = 1
    EQUAL_RANGE = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


DoubleAxisScaleAndRange.__setattr__ = __enum_setattr
DoubleAxisScaleAndRange.__delattr__ = __enum_delattr
