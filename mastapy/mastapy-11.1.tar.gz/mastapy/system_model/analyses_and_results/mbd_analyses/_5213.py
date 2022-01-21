'''_5213.py

ShapeOfInitialAccelerationPeriodForRunUp
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_SHAPE_OF_INITIAL_ACCELERATION_PERIOD_FOR_RUN_UP = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'ShapeOfInitialAccelerationPeriodForRunUp')


__docformat__ = 'restructuredtext en'
__all__ = ('ShapeOfInitialAccelerationPeriodForRunUp',)


class ShapeOfInitialAccelerationPeriodForRunUp(Enum):
    '''ShapeOfInitialAccelerationPeriodForRunUp

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _SHAPE_OF_INITIAL_ACCELERATION_PERIOD_FOR_RUN_UP

    __hash__ = None

    QUADRATIC = 0
    CUBIC = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ShapeOfInitialAccelerationPeriodForRunUp.__setattr__ = __enum_setattr
ShapeOfInitialAccelerationPeriodForRunUp.__delattr__ = __enum_delattr
