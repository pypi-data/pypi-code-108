'''_397.py

ISO10300SingleFlankRatingHypoidMethodB2
'''


from mastapy._internal import constructor
from mastapy.gears.rating.iso_10300 import _399
from mastapy._internal.python_net import python_net_import

_ISO10300_SINGLE_FLANK_RATING_HYPOID_METHOD_B2 = python_net_import('SMT.MastaAPI.Gears.Rating.Iso10300', 'ISO10300SingleFlankRatingHypoidMethodB2')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO10300SingleFlankRatingHypoidMethodB2',)


class ISO10300SingleFlankRatingHypoidMethodB2(_399.ISO10300SingleFlankRatingMethodB2):
    '''ISO10300SingleFlankRatingHypoidMethodB2

    This is a mastapy class.
    '''

    TYPE = _ISO10300_SINGLE_FLANK_RATING_HYPOID_METHOD_B2

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO10300SingleFlankRatingHypoidMethodB2.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def intermediate_value_eta_d(self) -> 'float':
        '''float: 'IntermediateValueEtaD' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IntermediateValueEtaD

    @property
    def intermediate_value_eta_c(self) -> 'float':
        '''float: 'IntermediateValueEtaC' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IntermediateValueEtaC

    @property
    def intermediate_angle_beta_a(self) -> 'float':
        '''float: 'IntermediateAngleBetaA' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IntermediateAngleBetaA

    @property
    def intermediate_angle_different_between_beta_d_and_delta_alpha(self) -> 'float':
        '''float: 'IntermediateAngleDifferentBetweenBetaDAndDeltaAlpha' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IntermediateAngleDifferentBetweenBetaDAndDeltaAlpha

    @property
    def intermediate_angle_different_between_beta_c_and_delta_alpha(self) -> 'float':
        '''float: 'IntermediateAngleDifferentBetweenBetaCAndDeltaAlpha' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IntermediateAngleDifferentBetweenBetaCAndDeltaAlpha

    @property
    def intermediate_value_g1(self) -> 'float':
        '''float: 'IntermediateValueG1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IntermediateValueG1

    @property
    def wheel_angle_between_centreline_and_fillet_point_on_drive_side(self) -> 'float':
        '''float: 'WheelAngleBetweenCentrelineAndFilletPointOnDriveSide' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelAngleBetweenCentrelineAndFilletPointOnDriveSide

    @property
    def wheel_angle_between_centreline_and_fillet_point_on_coast_side(self) -> 'float':
        '''float: 'WheelAngleBetweenCentrelineAndFilletPointOnCoastSide' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelAngleBetweenCentrelineAndFilletPointOnCoastSide

    @property
    def wheel_angle_between_fillet_point(self) -> 'float':
        '''float: 'WheelAngleBetweenFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelAngleBetweenFilletPoint

    @property
    def vertical_distance_from_pitch_circle_to_fillet_point(self) -> 'float':
        '''float: 'VerticalDistanceFromPitchCircleToFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VerticalDistanceFromPitchCircleToFilletPoint

    @property
    def horizontal_distance_from_centreline_to_fillet_point(self) -> 'float':
        '''float: 'HorizontalDistanceFromCentrelineToFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HorizontalDistanceFromCentrelineToFilletPoint

    @property
    def generated_pressure_angle_of_wheel_at_fillet_point(self) -> 'float':
        '''float: 'GeneratedPressureAngleOfWheelAtFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GeneratedPressureAngleOfWheelAtFilletPoint

    @property
    def distance_from_centreline_to_tool_critical_drive_side_fillet_point(self) -> 'float':
        '''float: 'DistanceFromCentrelineToToolCriticalDriveSideFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DistanceFromCentrelineToToolCriticalDriveSideFilletPoint

    @property
    def distance_from_centreline_to_tool_critical_coast_side_fillet_point(self) -> 'float':
        '''float: 'DistanceFromCentrelineToToolCriticalCoastSideFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DistanceFromCentrelineToToolCriticalCoastSideFilletPoint

    @property
    def wheel_angle_between_centreline_and_critical_point_drive_side_fillet_point(self) -> 'float':
        '''float: 'WheelAngleBetweenCentrelineAndCriticalPointDriveSideFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelAngleBetweenCentrelineAndCriticalPointDriveSideFilletPoint

    @property
    def wheel_angle_between_centreline_and_critical_point_coast_side_fillet_point(self) -> 'float':
        '''float: 'WheelAngleBetweenCentrelineAndCriticalPointCoastSideFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelAngleBetweenCentrelineAndCriticalPointCoastSideFilletPoint

    @property
    def radius_from_tool_centre_to_critical_pinion_drive_side_fillet_point(self) -> 'float':
        '''float: 'RadiusFromToolCentreToCriticalPinionDriveSideFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RadiusFromToolCentreToCriticalPinionDriveSideFilletPoint

    @property
    def radius_from_tool_centre_to_critical_pinion_coast_side_fillet_point(self) -> 'float':
        '''float: 'RadiusFromToolCentreToCriticalPinionCoastSideFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RadiusFromToolCentreToCriticalPinionCoastSideFilletPoint

    @property
    def wheel_angle_from_centreline_to_tooth_surface_at_critical_fillet_point_on_drive_side(self) -> 'float':
        '''float: 'WheelAngleFromCentrelineToToothSurfaceAtCriticalFilletPointOnDriveSide' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelAngleFromCentrelineToToothSurfaceAtCriticalFilletPointOnDriveSide

    @property
    def wheel_angle_from_centreline_to_tooth_surface_at_critical_fillet_point_on_coast_side(self) -> 'float':
        '''float: 'WheelAngleFromCentrelineToToothSurfaceAtCriticalFilletPointOnCoastSide' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelAngleFromCentrelineToToothSurfaceAtCriticalFilletPointOnCoastSide

    @property
    def pinion_angle_from_centreline_to_tooth_surface_at_critical_drive_side_fillet_point(self) -> 'float':
        '''float: 'PinionAngleFromCentrelineToToothSurfaceAtCriticalDriveSideFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionAngleFromCentrelineToToothSurfaceAtCriticalDriveSideFilletPoint

    @property
    def pinion_angle_from_centreline_to_tooth_surface_at_critical_coast_side_fillet_point(self) -> 'float':
        '''float: 'PinionAngleFromCentrelineToToothSurfaceAtCriticalCoastSideFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionAngleFromCentrelineToToothSurfaceAtCriticalCoastSideFilletPoint

    @property
    def wheel_difference_angle_between_tool_and_surface_at_drive_side_fillet_point(self) -> 'float':
        '''float: 'WheelDifferenceAngleBetweenToolAndSurfaceAtDriveSideFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelDifferenceAngleBetweenToolAndSurfaceAtDriveSideFilletPoint

    @property
    def wheel_difference_angle_between_tool_and_surface_at_coast_side_fillet_point(self) -> 'float':
        '''float: 'WheelDifferenceAngleBetweenToolAndSurfaceAtCoastSideFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelDifferenceAngleBetweenToolAndSurfaceAtCoastSideFilletPoint

    @property
    def pinion_difference_angle_between_tool_and_surface_at_drive_side_fillet_point(self) -> 'float':
        '''float: 'PinionDifferenceAngleBetweenToolAndSurfaceAtDriveSideFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionDifferenceAngleBetweenToolAndSurfaceAtDriveSideFilletPoint

    @property
    def pinion_difference_angle_between_tool_and_surface_at_coast_side_fillet_point(self) -> 'float':
        '''float: 'PinionDifferenceAngleBetweenToolAndSurfaceAtCoastSideFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionDifferenceAngleBetweenToolAndSurfaceAtCoastSideFilletPoint

    @property
    def pinion_angle_unbalance_between_fillet_point(self) -> 'float':
        '''float: 'PinionAngleUnbalanceBetweenFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionAngleUnbalanceBetweenFilletPoint

    @property
    def pinion_angle_from_centreline_to_pinion_tip(self) -> 'float':
        '''float: 'PinionAngleFromCentrelineToPinionTip' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionAngleFromCentrelineToPinionTip

    @property
    def wheel_angle_from_pinion_tip_to_point_of_load_application(self) -> 'float':
        '''float: 'WheelAngleFromPinionTipToPointOfLoadApplication' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelAngleFromPinionTipToPointOfLoadApplication

    @property
    def deltar_3(self) -> 'float':
        '''float: 'Deltar3' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Deltar3

    @property
    def h3(self) -> 'float':
        '''float: 'H3' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.H3

    @property
    def h3o(self) -> 'float':
        '''float: 'H3o' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.H3o

    @property
    def pinion_angle_from_wheel_tip_to_point_of_load_application(self) -> 'float':
        '''float: 'PinionAngleFromWheelTipToPointOfLoadApplication' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionAngleFromWheelTipToPointOfLoadApplication

    @property
    def deltar_4(self) -> 'float':
        '''float: 'Deltar4' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Deltar4

    @property
    def h4(self) -> 'float':
        '''float: 'H4' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.H4

    @property
    def h4o(self) -> 'float':
        '''float: 'H4o' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.H4o

    @property
    def distance_from_pitch_circle_to_point_of_load_application(self) -> 'float':
        '''float: 'DistanceFromPitchCircleToPointOfLoadApplication' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DistanceFromPitchCircleToPointOfLoadApplication

    @property
    def angle_between_centreline_and_line_from_point_of_load_application_and_fillet_point_on_wheel(self) -> 'float':
        '''float: 'AngleBetweenCentrelineAndLineFromPointOfLoadApplicationAndFilletPointOnWheel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AngleBetweenCentrelineAndLineFromPointOfLoadApplicationAndFilletPointOnWheel

    @property
    def wheel_horizontal_distance_from_centreline_to_critical_fillet_point(self) -> 'float':
        '''float: 'WheelHorizontalDistanceFromCentrelineToCriticalFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelHorizontalDistanceFromCentrelineToCriticalFilletPoint

    @property
    def vertical_distance_from_pitch_circle_to_critical_fillet_point(self) -> 'float':
        '''float: 'VerticalDistanceFromPitchCircleToCriticalFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VerticalDistanceFromPitchCircleToCriticalFilletPoint

    @property
    def wheel_load_height_at_weakest_section(self) -> 'float':
        '''float: 'WheelLoadHeightAtWeakestSection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelLoadHeightAtWeakestSection

    @property
    def auxiliary_value_hn2o(self) -> 'float':
        '''float: 'AuxiliaryValueHN2o' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxiliaryValueHN2o

    @property
    def wheel_tooth_strength_factor(self) -> 'float':
        '''float: 'WheelToothStrengthFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelToothStrengthFactor

    @property
    def pinion_angle_from_pitch_to_point_of_load_application(self) -> 'float':
        '''float: 'PinionAngleFromPitchToPointOfLoadApplication' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionAngleFromPitchToPointOfLoadApplication

    @property
    def pinion_pressure_angle_at_point_of_load_application(self) -> 'float':
        '''float: 'PinionPressureAngleAtPointOfLoadApplication' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionPressureAngleAtPointOfLoadApplication

    @property
    def pinion_radial_distance_to_point_of_load_application(self) -> 'float':
        '''float: 'PinionRadialDistanceToPointOfLoadApplication' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionRadialDistanceToPointOfLoadApplication

    @property
    def wheel_angle_between_centreline_and_pinion_fillet(self) -> 'float':
        '''float: 'WheelAngleBetweenCentrelineAndPinionFillet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelAngleBetweenCentrelineAndPinionFillet

    @property
    def deltar_5(self) -> 'float':
        '''float: 'Deltar5' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Deltar5

    @property
    def mu_d2(self) -> 'float':
        '''float: 'MuD2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MuD2

    @property
    def mu_d(self) -> 'float':
        '''float: 'MuD' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MuD

    @property
    def alpha_do(self) -> 'float':
        '''float: 'AlphaDo' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AlphaDo

    @property
    def pinion_angle_between_centreline_and_pinion_fillet(self) -> 'float':
        '''float: 'PinionAngleBetweenCentrelineAndPinionFillet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionAngleBetweenCentrelineAndPinionFillet

    @property
    def wheel_rotation_through_path_of_action(self) -> 'float':
        '''float: 'WheelRotationThroughPathOfAction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelRotationThroughPathOfAction

    @property
    def wheel_angle_difference_between_path_of_action_and_tooth_surface_at_pinion_fillet(self) -> 'float':
        '''float: 'WheelAngleDifferenceBetweenPathOfActionAndToothSurfaceAtPinionFillet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelAngleDifferenceBetweenPathOfActionAndToothSurfaceAtPinionFillet

    @property
    def wheel_radius_to_pinion_fillet_point(self) -> 'float':
        '''float: 'WheelRadiusToPinionFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelRadiusToPinionFilletPoint

    @property
    def pinion_angle_to_fillet_point(self) -> 'float':
        '''float: 'PinionAngleToFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionAngleToFilletPoint

    @property
    def pinion_radius_to_fillet_point(self) -> 'float':
        '''float: 'PinionRadiusToFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionRadiusToFilletPoint

    @property
    def pinion_angle_from_centreline_to_fillet_point(self) -> 'float':
        '''float: 'PinionAngleFromCentrelineToFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionAngleFromCentrelineToFilletPoint

    @property
    def angle_between_centreline_and_line_from_point_of_load_application_and_fillet_point_on_pinion(self) -> 'float':
        '''float: 'AngleBetweenCentrelineAndLineFromPointOfLoadApplicationAndFilletPointOnPinion' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AngleBetweenCentrelineAndLineFromPointOfLoadApplicationAndFilletPointOnPinion

    @property
    def pinion_horizontal_distance_to_critical_fillet_point(self) -> 'float':
        '''float: 'PinionHorizontalDistanceToCriticalFilletPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionHorizontalDistanceToCriticalFilletPoint

    @property
    def pinion_load_height_at_weakest_section(self) -> 'float':
        '''float: 'PinionLoadHeightAtWeakestSection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionLoadHeightAtWeakestSection

    @property
    def auxiliary_value_hn1o(self) -> 'float':
        '''float: 'AuxiliaryValueHN1o' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxiliaryValueHN1o

    @property
    def pinion_tooth_strength_factor(self) -> 'float':
        '''float: 'PinionToothStrengthFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionToothStrengthFactor

    @property
    def tooth_form_factor_for_hypoid_gear(self) -> 'float':
        '''float: 'ToothFormFactorForHypoidGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothFormFactorForHypoidGear

    @property
    def mean_face_width(self) -> 'float':
        '''float: 'MeanFaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanFaceWidth

    @property
    def contact_shift_due_to_load_for_pinion(self) -> 'float':
        '''float: 'ContactShiftDueToLoadForPinion' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactShiftDueToLoadForPinion

    @property
    def contact_shift_due_to_load_for_wheel(self) -> 'float':
        '''float: 'ContactShiftDueToLoadForWheel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactShiftDueToLoadForWheel

    @property
    def transverse_radius_to_point_of_load_application_for_pinion(self) -> 'float':
        '''float: 'TransverseRadiusToPointOfLoadApplicationForPinion' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseRadiusToPointOfLoadApplicationForPinion

    @property
    def transverse_radius_to_point_of_load_application_for_wheel(self) -> 'float':
        '''float: 'TransverseRadiusToPointOfLoadApplicationForWheel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseRadiusToPointOfLoadApplicationForWheel
