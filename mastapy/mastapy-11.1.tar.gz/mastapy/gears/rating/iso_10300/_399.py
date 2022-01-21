'''_399.py

ISO10300SingleFlankRatingMethodB2
'''


from mastapy._internal import constructor
from mastapy.gears.rating.iso_10300 import _395
from mastapy.gears.rating.virtual_cylindrical_gears import _357
from mastapy._internal.python_net import python_net_import

_ISO10300_SINGLE_FLANK_RATING_METHOD_B2 = python_net_import('SMT.MastaAPI.Gears.Rating.Iso10300', 'ISO10300SingleFlankRatingMethodB2')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO10300SingleFlankRatingMethodB2',)


class ISO10300SingleFlankRatingMethodB2(_395.ISO10300SingleFlankRating['_357.VirtualCylindricalGearISO10300MethodB2']):
    '''ISO10300SingleFlankRatingMethodB2

    This is a mastapy class.
    '''

    TYPE = _ISO10300_SINGLE_FLANK_RATING_METHOD_B2

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO10300SingleFlankRatingMethodB2.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def permissible_contact_stress_method_b2(self) -> 'float':
        '''float: 'PermissibleContactStressMethodB2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleContactStressMethodB2

    @property
    def safety_factor_contact_for_method_b2(self) -> 'float':
        '''float: 'SafetyFactorContactForMethodB2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorContactForMethodB2

    @property
    def cos_pressure_angle_at_point_of_load_application(self) -> 'float':
        '''float: 'CosPressureAngleAtPointOfLoadApplication' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CosPressureAngleAtPointOfLoadApplication

    @property
    def pressure_angle_at_point_of_load_application(self) -> 'float':
        '''float: 'PressureAngleAtPointOfLoadApplication' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PressureAngleAtPointOfLoadApplication

    @property
    def radius_of_curvature_difference_between_point_of_load_and_mean_point(self) -> 'float':
        '''float: 'RadiusOfCurvatureDifferenceBetweenPointOfLoadAndMeanPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RadiusOfCurvatureDifferenceBetweenPointOfLoadAndMeanPoint

    @property
    def contact_stress_adjustment_factor(self) -> 'float':
        '''float: 'ContactStressAdjustmentFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactStressAdjustmentFactor

    @property
    def tooth_root_stress_method_b2(self) -> 'float':
        '''float: 'ToothRootStressMethodB2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothRootStressMethodB2

    @property
    def nominal_value_of_root_stress_method_b2(self) -> 'float':
        '''float: 'NominalValueOfRootStressMethodB2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalValueOfRootStressMethodB2

    @property
    def combined_geometry_factor(self) -> 'float':
        '''float: 'CombinedGeometryFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CombinedGeometryFactor

    @property
    def permissible_tooth_root_stress_method_b2(self) -> 'float':
        '''float: 'PermissibleToothRootStressMethodB2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleToothRootStressMethodB2

    @property
    def safety_factor_bending_for_method_b2(self) -> 'float':
        '''float: 'SafetyFactorBendingForMethodB2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorBendingForMethodB2

    @property
    def geometry_factor(self) -> 'float':
        '''float: 'GeometryFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GeometryFactor

    @property
    def relative_fillet_radius_at_root_of_tooth(self) -> 'float':
        '''float: 'RelativeFilletRadiusAtRootOfTooth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeFilletRadiusAtRootOfTooth

    @property
    def stress_concentration_and_correction_factor(self) -> 'float':
        '''float: 'StressConcentrationAndCorrectionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressConcentrationAndCorrectionFactor

    @property
    def L(self) -> 'float':
        '''float: 'L' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.L

    @property
    def m(self) -> 'float':
        '''float: 'M' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.M

    @property
    def o(self) -> 'float':
        '''float: 'O' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.O

    @property
    def inertia_factor(self) -> 'float':
        '''float: 'InertiaFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InertiaFactor

    @property
    def projected_length_of_the_instantaneous_contact_line_in_the_tooth_lengthwise_direction(self) -> 'float':
        '''float: 'ProjectedLengthOfTheInstantaneousContactLineInTheToothLengthwiseDirection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProjectedLengthOfTheInstantaneousContactLineInTheToothLengthwiseDirection

    @property
    def toe_increment(self) -> 'float':
        '''float: 'ToeIncrement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToeIncrement

    @property
    def heel_increment(self) -> 'float':
        '''float: 'HeelIncrement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HeelIncrement

    @property
    def toe_increment_delta_bi(self) -> 'float':
        '''float: 'ToeIncrementDeltaBi' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToeIncrementDeltaBi

    @property
    def heel_increment_delta_be(self) -> 'float':
        '''float: 'HeelIncrementDeltaBe' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HeelIncrementDeltaBe

    @property
    def effective_face_width(self) -> 'float':
        '''float: 'EffectiveFaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EffectiveFaceWidth

    @property
    def root_stress_adjustment_factor(self) -> 'float':
        '''float: 'RootStressAdjustmentFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RootStressAdjustmentFactor

    @property
    def relative_surface_condition_factor_for_method_b2(self) -> 'float':
        '''float: 'RelativeSurfaceConditionFactorForMethodB2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeSurfaceConditionFactorForMethodB2

    @property
    def relative_notch_sensitivity_factor(self) -> 'float':
        '''float: 'RelativeNotchSensitivityFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeNotchSensitivityFactor
