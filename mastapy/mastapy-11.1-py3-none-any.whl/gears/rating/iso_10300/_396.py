'''_396.py

ISO10300SingleFlankRatingBevelMethodB2
'''


from mastapy._internal import constructor
from mastapy.gears.rating.iso_10300 import _399
from mastapy._internal.python_net import python_net_import

_ISO10300_SINGLE_FLANK_RATING_BEVEL_METHOD_B2 = python_net_import('SMT.MastaAPI.Gears.Rating.Iso10300', 'ISO10300SingleFlankRatingBevelMethodB2')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO10300SingleFlankRatingBevelMethodB2',)


class ISO10300SingleFlankRatingBevelMethodB2(_399.ISO10300SingleFlankRatingMethodB2):
    '''ISO10300SingleFlankRatingBevelMethodB2

    This is a mastapy class.
    '''

    TYPE = _ISO10300_SINGLE_FLANK_RATING_BEVEL_METHOD_B2

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO10300SingleFlankRatingBevelMethodB2.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def point_of_load_application_on_path_of_action_for_maximum_root_stress_for_straight_bevel_and_zerol_bevel_gear(self) -> 'float':
        '''float: 'PointOfLoadApplicationOnPathOfActionForMaximumRootStressForStraightBevelAndZerolBevelGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PointOfLoadApplicationOnPathOfActionForMaximumRootStressForStraightBevelAndZerolBevelGear

    @property
    def point_of_load_application_on_path_of_action_for_maximum_root_stress_for_spiral_bevel_pinions(self) -> 'float':
        '''float: 'PointOfLoadApplicationOnPathOfActionForMaximumRootStressForSpiralBevelPinions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PointOfLoadApplicationOnPathOfActionForMaximumRootStressForSpiralBevelPinions

    @property
    def point_of_load_application_on_path_of_action_for_maximum_root_stress_for_spiral_bevel_wheels(self) -> 'float':
        '''float: 'PointOfLoadApplicationOnPathOfActionForMaximumRootStressForSpiralBevelWheels' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PointOfLoadApplicationOnPathOfActionForMaximumRootStressForSpiralBevelWheels

    @property
    def distance_from_mean_section_to_point_of_load_application_for_straight_bevel_and_zerol_bevel_gear(self) -> 'float':
        '''float: 'DistanceFromMeanSectionToPointOfLoadApplicationForStraightBevelAndZerolBevelGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DistanceFromMeanSectionToPointOfLoadApplicationForStraightBevelAndZerolBevelGear

    @property
    def distance_from_mean_section_to_point_of_load_application_for_spiral_bevel_pinions(self) -> 'float':
        '''float: 'DistanceFromMeanSectionToPointOfLoadApplicationForSpiralBevelPinions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DistanceFromMeanSectionToPointOfLoadApplicationForSpiralBevelPinions

    @property
    def distance_from_mean_section_to_point_of_load_application_for_spiral_bevel_wheels(self) -> 'float':
        '''float: 'DistanceFromMeanSectionToPointOfLoadApplicationForSpiralBevelWheels' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DistanceFromMeanSectionToPointOfLoadApplicationForSpiralBevelWheels

    @property
    def normal_pressure_angle_at_point_of_load(self) -> 'float':
        '''float: 'NormalPressureAngleAtPointOfLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalPressureAngleAtPointOfLoad

    @property
    def one_half_of_angle_subtended_by_normal_circular_tooth_thickness_at_point_of_load_application(self) -> 'float':
        '''float: 'OneHalfOfAngleSubtendedByNormalCircularToothThicknessAtPointOfLoadApplication' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OneHalfOfAngleSubtendedByNormalCircularToothThicknessAtPointOfLoadApplication

    @property
    def relative_distance_from_pitch_circle_to_pinion_point_of_load_and_the_wheel_tooth_centreline(self) -> 'float':
        '''float: 'RelativeDistanceFromPitchCircleToPinionPointOfLoadAndTheWheelToothCentreline' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeDistanceFromPitchCircleToPinionPointOfLoadAndTheWheelToothCentreline

    @property
    def alphah(self) -> 'float':
        '''float: 'Alphah' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Alphah

    @property
    def mean_transverse_radius_to_point_of_load_application(self) -> 'float':
        '''float: 'MeanTransverseRadiusToPointOfLoadApplication' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanTransverseRadiusToPointOfLoadApplication

    @property
    def g0(self) -> 'float':
        '''float: 'G0' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.G0

    @property
    def gyb(self) -> 'float':
        '''float: 'Gyb' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Gyb

    @property
    def initial_guess_gf_0(self) -> 'float':
        '''float: 'InitialGuessGf0' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InitialGuessGf0

    @property
    def assumed_angle_in_locating_weakest_section(self) -> 'float':
        '''float: 'AssumedAngleInLocatingWeakestSection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AssumedAngleInLocatingWeakestSection

    @property
    def gxb(self) -> 'float':
        '''float: 'Gxb' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Gxb

    @property
    def gza(self) -> 'float':
        '''float: 'Gza' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Gza

    @property
    def gzb(self) -> 'float':
        '''float: 'Gzb' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Gzb

    @property
    def angle_between_tangent_of_root_fillet_at_weakest_point_and_centreline_of_tooth(self) -> 'float':
        '''float: 'AngleBetweenTangentOfRootFilletAtWeakestPointAndCentrelineOfTooth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AngleBetweenTangentOfRootFilletAtWeakestPointAndCentrelineOfTooth

    @property
    def one_half_tooth_thickness_at_critical_section(self) -> 'float':
        '''float: 'OneHalfToothThicknessAtCriticalSection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OneHalfToothThicknessAtCriticalSection

    @property
    def load_height_from_critical_section(self) -> 'float':
        '''float: 'LoadHeightFromCriticalSection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadHeightFromCriticalSection

    @property
    def iteration_balance_value_for_tooth_form_factor(self) -> 'float':
        '''float: 'IterationBalanceValueForToothFormFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IterationBalanceValueForToothFormFactor

    @property
    def tooth_strength_factor(self) -> 'float':
        '''float: 'ToothStrengthFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothStrengthFactor

    @property
    def tooth_form_factor_for_bevel_gear(self) -> 'float':
        '''float: 'ToothFormFactorForBevelGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothFormFactorForBevelGear
