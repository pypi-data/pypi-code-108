'''_776.py

WheelRoughCutter
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.conical import _1100
from mastapy._internal.python_net import python_net_import

_WHEEL_ROUGH_CUTTER = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel.Cutters', 'WheelRoughCutter')


__docformat__ = 'restructuredtext en'
__all__ = ('WheelRoughCutter',)


class WheelRoughCutter(_1100.ConicalGearCutter):
    '''WheelRoughCutter

    This is a mastapy class.
    '''

    TYPE = _WHEEL_ROUGH_CUTTER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WheelRoughCutter.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def delta_bg(self) -> 'float':
        '''float: 'DeltaBG' is the original name of this property.'''

        return self.wrapped.DeltaBG

    @delta_bg.setter
    def delta_bg(self, value: 'float'):
        self.wrapped.DeltaBG = float(value) if value else 0.0

    @property
    def stock_allowance(self) -> 'float':
        '''float: 'StockAllowance' is the original name of this property.'''

        return self.wrapped.StockAllowance

    @stock_allowance.setter
    def stock_allowance(self, value: 'float'):
        self.wrapped.StockAllowance = float(value) if value else 0.0

    @property
    def point_width(self) -> 'float':
        '''float: 'PointWidth' is the original name of this property.'''

        return self.wrapped.PointWidth

    @point_width.setter
    def point_width(self, value: 'float'):
        self.wrapped.PointWidth = float(value) if value else 0.0

    @property
    def inner_blade_point_radius_convex(self) -> 'float':
        '''float: 'InnerBladePointRadiusConvex' is the original name of this property.'''

        return self.wrapped.InnerBladePointRadiusConvex

    @inner_blade_point_radius_convex.setter
    def inner_blade_point_radius_convex(self, value: 'float'):
        self.wrapped.InnerBladePointRadiusConvex = float(value) if value else 0.0

    @property
    def outer_blade_point_radius_concave(self) -> 'float':
        '''float: 'OuterBladePointRadiusConcave' is the original name of this property.'''

        return self.wrapped.OuterBladePointRadiusConcave

    @outer_blade_point_radius_concave.setter
    def outer_blade_point_radius_concave(self, value: 'float'):
        self.wrapped.OuterBladePointRadiusConcave = float(value) if value else 0.0
