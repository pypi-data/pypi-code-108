'''_603.py

ChartType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CHART_TYPE = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.PlungeShaving', 'ChartType')


__docformat__ = 'restructuredtext en'
__all__ = ('ChartType',)


class ChartType(Enum):
    '''ChartType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CHART_TYPE

    __hash__ = None

    FLANK_PROFILE = 0
    LEAD_MODIFICATIONS = 1
    SHAVER_PROFILE_MODIFICATIONS_IN_PLANE = 2
    SHAVER_RADIUS_RANGE = 3
    SHAVER_TOOTH_SURFACE = 4
    REAL_SHAVED_GEAR_TOOTH_SURFACE = 5
    REAL_SHAVED_GEAR_LEAD_MODIFICATIONS = 6
    REAL_SHAVED_GEAR_PROFILE_MODIFICATIONS_IN_PLANE = 7
    REAL_SHAVED_GEAR_TOTAL_FLANK_MODIFICATION = 8
    DIFFERENCE_BETWEEN_INPUT_GEAR_AND_REAL_SHAVED_GEAR = 9
    DIFFERENCE_BETWEEN_INPUT_GEAR_AND_REAL_SHAVED_GEAR_IN_PLANE = 10


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ChartType.__setattr__ = __enum_setattr
ChartType.__delattr__ = __enum_delattr
