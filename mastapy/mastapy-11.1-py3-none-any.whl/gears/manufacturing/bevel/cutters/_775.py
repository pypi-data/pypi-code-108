'''_775.py

WheelFinishCutter
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.conical import _1100
from mastapy._internal.python_net import python_net_import

_WHEEL_FINISH_CUTTER = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel.Cutters', 'WheelFinishCutter')


__docformat__ = 'restructuredtext en'
__all__ = ('WheelFinishCutter',)


class WheelFinishCutter(_1100.ConicalGearCutter):
    '''WheelFinishCutter

    This is a mastapy class.
    '''

    TYPE = _WHEEL_FINISH_CUTTER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WheelFinishCutter.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def point_width(self) -> 'float':
        '''float: 'PointWidth' is the original name of this property.'''

        return self.wrapped.PointWidth

    @point_width.setter
    def point_width(self, value: 'float'):
        self.wrapped.PointWidth = float(value) if value else 0.0
