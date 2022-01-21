'''_1110.py

DummyConicalGearCutter
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.conical import _1100
from mastapy._internal.python_net import python_net_import

_DUMMY_CONICAL_GEAR_CUTTER = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Conical', 'DummyConicalGearCutter')


__docformat__ = 'restructuredtext en'
__all__ = ('DummyConicalGearCutter',)


class DummyConicalGearCutter(_1100.ConicalGearCutter):
    '''DummyConicalGearCutter

    This is a mastapy class.
    '''

    TYPE = _DUMMY_CONICAL_GEAR_CUTTER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DummyConicalGearCutter.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def inner_edge_radius_convex(self) -> 'float':
        '''float: 'InnerEdgeRadiusConvex' is the original name of this property.'''

        return self.wrapped.InnerEdgeRadiusConvex

    @inner_edge_radius_convex.setter
    def inner_edge_radius_convex(self, value: 'float'):
        self.wrapped.InnerEdgeRadiusConvex = float(value) if value else 0.0

    @property
    def outer_edge_radius_concave(self) -> 'float':
        '''float: 'OuterEdgeRadiusConcave' is the original name of this property.'''

        return self.wrapped.OuterEdgeRadiusConcave

    @outer_edge_radius_concave.setter
    def outer_edge_radius_concave(self, value: 'float'):
        self.wrapped.OuterEdgeRadiusConcave = float(value) if value else 0.0

    @property
    def number_of_blade_groups(self) -> 'int':
        '''int: 'NumberOfBladeGroups' is the original name of this property.'''

        return self.wrapped.NumberOfBladeGroups

    @number_of_blade_groups.setter
    def number_of_blade_groups(self, value: 'int'):
        self.wrapped.NumberOfBladeGroups = int(value) if value else 0

    @property
    def finish_cutter_point_width(self) -> 'float':
        '''float: 'FinishCutterPointWidth' is the original name of this property.'''

        return self.wrapped.FinishCutterPointWidth

    @finish_cutter_point_width.setter
    def finish_cutter_point_width(self, value: 'float'):
        self.wrapped.FinishCutterPointWidth = float(value) if value else 0.0

    @property
    def radius(self) -> 'float':
        '''float: 'Radius' is the original name of this property.'''

        return self.wrapped.Radius

    @radius.setter
    def radius(self, value: 'float'):
        self.wrapped.Radius = float(value) if value else 0.0
