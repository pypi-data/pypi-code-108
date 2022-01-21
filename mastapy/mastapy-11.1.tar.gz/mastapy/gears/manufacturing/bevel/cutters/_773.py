'''_773.py

PinionFinishCutter
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.conical import _1100
from mastapy._internal.python_net import python_net_import

_PINION_FINISH_CUTTER = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel.Cutters', 'PinionFinishCutter')


__docformat__ = 'restructuredtext en'
__all__ = ('PinionFinishCutter',)


class PinionFinishCutter(_1100.ConicalGearCutter):
    '''PinionFinishCutter

    This is a mastapy class.
    '''

    TYPE = _PINION_FINISH_CUTTER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PinionFinishCutter.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def outer_blade_point_radius_concave(self) -> 'float':
        '''float: 'OuterBladePointRadiusConcave' is the original name of this property.'''

        return self.wrapped.OuterBladePointRadiusConcave

    @outer_blade_point_radius_concave.setter
    def outer_blade_point_radius_concave(self, value: 'float'):
        self.wrapped.OuterBladePointRadiusConcave = float(value) if value else 0.0

    @property
    def inner_blade_point_radius_convex(self) -> 'float':
        '''float: 'InnerBladePointRadiusConvex' is the original name of this property.'''

        return self.wrapped.InnerBladePointRadiusConvex

    @inner_blade_point_radius_convex.setter
    def inner_blade_point_radius_convex(self, value: 'float'):
        self.wrapped.InnerBladePointRadiusConvex = float(value) if value else 0.0

    @property
    def radius(self) -> 'float':
        '''float: 'Radius' is the original name of this property.'''

        return self.wrapped.Radius

    @radius.setter
    def radius(self, value: 'float'):
        self.wrapped.Radius = float(value) if value else 0.0
