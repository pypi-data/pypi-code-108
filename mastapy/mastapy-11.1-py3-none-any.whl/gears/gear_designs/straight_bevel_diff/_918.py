'''_918.py

StraightBevelDiffGearDesign
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.gears.gear_designs.bevel import _1132, _1127
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_DIFF_GEAR_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.StraightBevelDiff', 'StraightBevelDiffGearDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelDiffGearDesign',)


class StraightBevelDiffGearDesign(_1127.BevelGearDesign):
    '''StraightBevelDiffGearDesign

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_DIFF_GEAR_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelDiffGearDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def limited_point_width_large_end(self) -> 'float':
        '''float: 'LimitedPointWidthLargeEnd' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LimitedPointWidthLargeEnd

    @property
    def limited_point_width_small_end(self) -> 'float':
        '''float: 'LimitedPointWidthSmallEnd' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LimitedPointWidthSmallEnd

    @property
    def max_radius_interference(self) -> 'float':
        '''float: 'MaxRadiusInterference' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaxRadiusInterference

    @property
    def max_radius_cutter_blades(self) -> 'float':
        '''float: 'MaxRadiusCutterBlades' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaxRadiusCutterBlades

    @property
    def maximum_edge_radius(self) -> 'float':
        '''float: 'MaximumEdgeRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumEdgeRadius

    @property
    def edge_radius_from(self) -> '_1132.EdgeRadiusType':
        '''EdgeRadiusType: 'EdgeRadiusFrom' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.EdgeRadiusFrom)
        return constructor.new(_1132.EdgeRadiusType)(value) if value is not None else None

    @edge_radius_from.setter
    def edge_radius_from(self, value: '_1132.EdgeRadiusType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.EdgeRadiusFrom = value

    @property
    def outer_chordal_thickness(self) -> 'float':
        '''float: 'OuterChordalThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OuterChordalThickness

    @property
    def outer_chordal_addendum(self) -> 'float':
        '''float: 'OuterChordalAddendum' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OuterChordalAddendum

    @property
    def edge_radius(self) -> 'float':
        '''float: 'EdgeRadius' is the original name of this property.'''

        return self.wrapped.EdgeRadius

    @edge_radius.setter
    def edge_radius(self, value: 'float'):
        self.wrapped.EdgeRadius = float(value) if value else 0.0

    @property
    def allowable_performance_bending_stress(self) -> 'float':
        '''float: 'AllowablePerformanceBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowablePerformanceBendingStress

    @property
    def allowable_peak_bending_stress(self) -> 'float':
        '''float: 'AllowablePeakBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowablePeakBendingStress
