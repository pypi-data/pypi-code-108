'''_1303.py

DynamicsResponse3DChartType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_DYNAMICS_RESPONSE_3D_CHART_TYPE = python_net_import('SMT.MastaAPI.MathUtility', 'DynamicsResponse3DChartType')


__docformat__ = 'restructuredtext en'
__all__ = ('DynamicsResponse3DChartType',)


class DynamicsResponse3DChartType(Enum):
    '''DynamicsResponse3DChartType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _DYNAMICS_RESPONSE_3D_CHART_TYPE

    __hash__ = None

    WATERFALL_FREQUENCY_AND_SPEED = 0
    ORDER_MAP_ORDER_AND_SPEED = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


DynamicsResponse3DChartType.__setattr__ = __enum_setattr
DynamicsResponse3DChartType.__delattr__ = __enum_delattr
