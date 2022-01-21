'''_1137.py

ToothThicknessSpecificationMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_TOOTH_THICKNESS_SPECIFICATION_METHOD = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Bevel', 'ToothThicknessSpecificationMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('ToothThicknessSpecificationMethod',)


class ToothThicknessSpecificationMethod(Enum):
    '''ToothThicknessSpecificationMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _TOOTH_THICKNESS_SPECIFICATION_METHOD

    __hash__ = None

    CIRCULAR_THICKNESS_FACTOR = 0
    WHEEL_MEAN_SLOT_WIDTH = 1
    WHEEL_FINISH_CUTTER_POINT_WIDTH = 2
    PINION_MEAN_TRANSVERSE_CIRCULAR_THICKNESS = 3
    PINION_OUTER_TRANSVERSE_CIRCULAR_THICKNESS = 4
    EQUAL_STRESS = 5
    EQUAL_LIFE = 6
    STRENGTH_FACTOR = 7


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ToothThicknessSpecificationMethod.__setattr__ = __enum_setattr
ToothThicknessSpecificationMethod.__delattr__ = __enum_delattr
