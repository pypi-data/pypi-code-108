'''_392.py

ISO10300MeshSingleFlankRatingMethodB2
'''


from mastapy._internal import constructor
from mastapy.gears.rating.virtual_cylindrical_gears import (
    _360, _346, _349, _357
)
from mastapy._internal.cast_exception import CastException
from mastapy.gears.rating.iso_10300 import _388
from mastapy._internal.python_net import python_net_import

_ISO10300_MESH_SINGLE_FLANK_RATING_METHOD_B2 = python_net_import('SMT.MastaAPI.Gears.Rating.Iso10300', 'ISO10300MeshSingleFlankRatingMethodB2')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO10300MeshSingleFlankRatingMethodB2',)


class ISO10300MeshSingleFlankRatingMethodB2(_388.ISO10300MeshSingleFlankRating['_357.VirtualCylindricalGearISO10300MethodB2']):
    '''ISO10300MeshSingleFlankRatingMethodB2

    This is a mastapy class.
    '''

    TYPE = _ISO10300_MESH_SINGLE_FLANK_RATING_METHOD_B2

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO10300MeshSingleFlankRatingMethodB2.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def transverse_load_factors_for_contact_method_b2(self) -> 'float':
        '''float: 'TransverseLoadFactorsForContactMethodB2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseLoadFactorsForContactMethodB2

    @property
    def transverse_load_factors_for_bending_method_b2(self) -> 'float':
        '''float: 'TransverseLoadFactorsForBendingMethodB2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseLoadFactorsForBendingMethodB2

    @property
    def contact_stress_method_b2(self) -> 'float':
        '''float: 'ContactStressMethodB2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactStressMethodB2

    @property
    def nominal_value_of_contact_stress_method_b2(self) -> 'float':
        '''float: 'NominalValueOfContactStressMethodB2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalValueOfContactStressMethodB2

    @property
    def radius_of_curvature_change(self) -> 'float':
        '''float: 'RadiusOfCurvatureChange' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RadiusOfCurvatureChange

    @property
    def relative_length_of_action_within_the_contact_ellipse(self) -> 'float':
        '''float: 'RelativeLengthOfActionWithinTheContactEllipse' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeLengthOfActionWithinTheContactEllipse

    @property
    def yi_for_bevel_and_zerol_bevel_gear(self) -> 'float':
        '''float: 'YIForBevelAndZerolBevelGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.YIForBevelAndZerolBevelGear

    @property
    def length_of_action_at_critical_point(self) -> 'float':
        '''float: 'LengthOfActionAtCriticalPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LengthOfActionAtCriticalPoint

    @property
    def length_of_action_considering_adjacent_teeth(self) -> 'float':
        '''float: 'LengthOfActionConsideringAdjacentTeeth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LengthOfActionConsideringAdjacentTeeth

    @property
    def load_sharing_ratio_for_pitting_method_b2(self) -> 'float':
        '''float: 'LoadSharingRatioForPittingMethodB2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadSharingRatioForPittingMethodB2

    @property
    def length_of_contact_line(self) -> 'float':
        '''float: 'LengthOfContactLine' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LengthOfContactLine

    @property
    def position_change_alone_path_of_contact(self) -> 'float':
        '''float: 'PositionChangeAlonePathOfContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PositionChangeAlonePathOfContact

    @property
    def intermediate_value_x(self) -> 'float':
        '''float: 'IntermediateValueX' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IntermediateValueX

    @property
    def pinion_profile_radius_of_curvature(self) -> 'float':
        '''float: 'PinionProfileRadiusOfCurvature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionProfileRadiusOfCurvature

    @property
    def wheel_profile_radius_of_curvature(self) -> 'float':
        '''float: 'WheelProfileRadiusOfCurvature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelProfileRadiusOfCurvature

    @property
    def relative_radius_of_profile_curvature_between_pinion_and_wheel(self) -> 'float':
        '''float: 'RelativeRadiusOfProfileCurvatureBetweenPinionAndWheel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeRadiusOfProfileCurvatureBetweenPinionAndWheel

    @property
    def inertia_factor_value_x(self) -> 'float':
        '''float: 'InertiaFactorValueX' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InertiaFactorValueX

    @property
    def pitting_resistance_geometry_factor(self) -> 'float':
        '''float: 'PittingResistanceGeometryFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PittingResistanceGeometryFactor

    @property
    def yi_for_hypoid_gear(self) -> 'float':
        '''float: 'YIForHypoidGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.YIForHypoidGear

    @property
    def yi(self) -> 'float':
        '''float: 'YI' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.YI

    @property
    def face_width_factor(self) -> 'float':
        '''float: 'FaceWidthFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceWidthFactor

    @property
    def contact_stress_adjustment_factor(self) -> 'float':
        '''float: 'ContactStressAdjustmentFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactStressAdjustmentFactor

    @property
    def relative_length_of_action_ellipse_contact(self) -> 'float':
        '''float: 'RelativeLengthOfActionEllipseContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeLengthOfActionEllipseContact

    @property
    def relative_length_of_action_ellipse_contact_for_statically_loaded_straight_bevel_and_zerol_bevel_gears(self) -> 'float':
        '''float: 'RelativeLengthOfActionEllipseContactForStaticallyLoadedStraightBevelAndZerolBevelGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeLengthOfActionEllipseContactForStaticallyLoadedStraightBevelAndZerolBevelGears

    @property
    def load_sharing_ratio_for_bending_method_b2(self) -> 'float':
        '''float: 'LoadSharingRatioForBendingMethodB2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadSharingRatioForBendingMethodB2

    @property
    def virtual_cylindrical_gear_set_method_b2(self) -> '_360.VirtualCylindricalGearSetISO10300MethodB2':
        '''VirtualCylindricalGearSetISO10300MethodB2: 'VirtualCylindricalGearSetMethodB2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _360.VirtualCylindricalGearSetISO10300MethodB2.TYPE not in self.wrapped.VirtualCylindricalGearSetMethodB2.__class__.__mro__:
            raise CastException('Failed to cast virtual_cylindrical_gear_set_method_b2 to VirtualCylindricalGearSetISO10300MethodB2. Expected: {}.'.format(self.wrapped.VirtualCylindricalGearSetMethodB2.__class__.__qualname__))

        return constructor.new_override(self.wrapped.VirtualCylindricalGearSetMethodB2.__class__)(self.wrapped.VirtualCylindricalGearSetMethodB2) if self.wrapped.VirtualCylindricalGearSetMethodB2 is not None else None

    @property
    def virtual_cylindrical_gear_set_method_b2_of_type_bevel_virtual_cylindrical_gear_set_iso10300_method_b2(self) -> '_346.BevelVirtualCylindricalGearSetISO10300MethodB2':
        '''BevelVirtualCylindricalGearSetISO10300MethodB2: 'VirtualCylindricalGearSetMethodB2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _346.BevelVirtualCylindricalGearSetISO10300MethodB2.TYPE not in self.wrapped.VirtualCylindricalGearSetMethodB2.__class__.__mro__:
            raise CastException('Failed to cast virtual_cylindrical_gear_set_method_b2 to BevelVirtualCylindricalGearSetISO10300MethodB2. Expected: {}.'.format(self.wrapped.VirtualCylindricalGearSetMethodB2.__class__.__qualname__))

        return constructor.new_override(self.wrapped.VirtualCylindricalGearSetMethodB2.__class__)(self.wrapped.VirtualCylindricalGearSetMethodB2) if self.wrapped.VirtualCylindricalGearSetMethodB2 is not None else None

    @property
    def virtual_cylindrical_gear_set_method_b2_of_type_hypoid_virtual_cylindrical_gear_set_iso10300_method_b2(self) -> '_349.HypoidVirtualCylindricalGearSetISO10300MethodB2':
        '''HypoidVirtualCylindricalGearSetISO10300MethodB2: 'VirtualCylindricalGearSetMethodB2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _349.HypoidVirtualCylindricalGearSetISO10300MethodB2.TYPE not in self.wrapped.VirtualCylindricalGearSetMethodB2.__class__.__mro__:
            raise CastException('Failed to cast virtual_cylindrical_gear_set_method_b2 to HypoidVirtualCylindricalGearSetISO10300MethodB2. Expected: {}.'.format(self.wrapped.VirtualCylindricalGearSetMethodB2.__class__.__qualname__))

        return constructor.new_override(self.wrapped.VirtualCylindricalGearSetMethodB2.__class__)(self.wrapped.VirtualCylindricalGearSetMethodB2) if self.wrapped.VirtualCylindricalGearSetMethodB2 is not None else None
