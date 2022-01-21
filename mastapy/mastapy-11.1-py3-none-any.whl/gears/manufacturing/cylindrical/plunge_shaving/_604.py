'''_604.py

GearPointCalculationError
'''


from mastapy.gears.manufacturing.cylindrical.plunge_shaving import _602
from mastapy._internal.python_net import python_net_import

_GEAR_POINT_CALCULATION_ERROR = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.PlungeShaving', 'GearPointCalculationError')


__docformat__ = 'restructuredtext en'
__all__ = ('GearPointCalculationError',)


class GearPointCalculationError(_602.CalculationError):
    '''GearPointCalculationError

    This is a mastapy class.
    '''

    TYPE = _GEAR_POINT_CALCULATION_ERROR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearPointCalculationError.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
