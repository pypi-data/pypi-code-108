'''_1138.py

WheelFinishCutterPointWidthRestrictionMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_WHEEL_FINISH_CUTTER_POINT_WIDTH_RESTRICTION_METHOD = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Bevel', 'WheelFinishCutterPointWidthRestrictionMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('WheelFinishCutterPointWidthRestrictionMethod',)


class WheelFinishCutterPointWidthRestrictionMethod(Enum):
    '''WheelFinishCutterPointWidthRestrictionMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _WHEEL_FINISH_CUTTER_POINT_WIDTH_RESTRICTION_METHOD

    __hash__ = None

    NONE = 0
    TO_NEAREST_01_MM = 1
    TO_NEAREST_0005_INCHES = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


WheelFinishCutterPointWidthRestrictionMethod.__setattr__ = __enum_setattr
WheelFinishCutterPointWidthRestrictionMethod.__delattr__ = __enum_delattr
