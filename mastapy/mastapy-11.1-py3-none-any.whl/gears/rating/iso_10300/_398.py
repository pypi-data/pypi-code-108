'''_398.py

ISO10300SingleFlankRatingMethodB1
'''


from mastapy._internal import constructor
from mastapy.gears.rating.iso_10300 import _395
from mastapy.gears.rating.virtual_cylindrical_gears import _356
from mastapy._internal.python_net import python_net_import

_ISO10300_SINGLE_FLANK_RATING_METHOD_B1 = python_net_import('SMT.MastaAPI.Gears.Rating.Iso10300', 'ISO10300SingleFlankRatingMethodB1')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO10300SingleFlankRatingMethodB1',)


class ISO10300SingleFlankRatingMethodB1(_395.ISO10300SingleFlankRating['_356.VirtualCylindricalGearISO10300MethodB1']):
    '''ISO10300SingleFlankRatingMethodB1

    This is a mastapy class.
    '''

    TYPE = _ISO10300_SINGLE_FLANK_RATING_METHOD_B1

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO10300SingleFlankRatingMethodB1.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def permissible_contact_stress_method_b1(self) -> 'float':
        '''float: 'PermissibleContactStressMethodB1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleContactStressMethodB1

    @property
    def permissible_contact_stress_use_bevel_slip_factor_method_b1(self) -> 'float':
        '''float: 'PermissibleContactStressUseBevelSlipFactorMethodB1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleContactStressUseBevelSlipFactorMethodB1

    @property
    def safety_factor_contact_for_method_b1(self) -> 'float':
        '''float: 'SafetyFactorContactForMethodB1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorContactForMethodB1

    @property
    def safety_factor_contact_use_bevel_slip_factor_for_method_b1(self) -> 'float':
        '''float: 'SafetyFactorContactUseBevelSlipFactorForMethodB1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorContactUseBevelSlipFactorForMethodB1

    @property
    def tooth_root_stress_method_b1(self) -> 'float':
        '''float: 'ToothRootStressMethodB1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothRootStressMethodB1

    @property
    def nominal_value_of_root_stress_method_b1(self) -> 'float':
        '''float: 'NominalValueOfRootStressMethodB1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalValueOfRootStressMethodB1

    @property
    def permissible_tooth_root_stress_method_b1(self) -> 'float':
        '''float: 'PermissibleToothRootStressMethodB1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleToothRootStressMethodB1

    @property
    def safety_factor_bending_for_method_b1(self) -> 'float':
        '''float: 'SafetyFactorBendingForMethodB1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorBendingForMethodB1

    @property
    def tooth_form_factor_for_generated_gear(self) -> 'float':
        '''float: 'ToothFormFactorForGeneratedGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothFormFactorForGeneratedGear

    @property
    def auxiliary_quantities_e_for_generated_gear_drive_flank(self) -> 'float':
        '''float: 'AuxiliaryQuantitiesEForGeneratedGearDriveFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxiliaryQuantitiesEForGeneratedGearDriveFlank

    @property
    def auxiliary_quantities_e_for_generated_gear_coast_flank(self) -> 'float':
        '''float: 'AuxiliaryQuantitiesEForGeneratedGearCoastFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxiliaryQuantitiesEForGeneratedGearCoastFlank

    @property
    def auxiliary_quantities_g_for_drive_side(self) -> 'float':
        '''float: 'AuxiliaryQuantitiesGForDriveSide' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxiliaryQuantitiesGForDriveSide

    @property
    def auxiliary_quantities_g_for_coast_side(self) -> 'float':
        '''float: 'AuxiliaryQuantitiesGForCoastSide' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxiliaryQuantitiesGForCoastSide

    @property
    def auxiliary_quantities_h_for_drive_side(self) -> 'float':
        '''float: 'AuxiliaryQuantitiesHForDriveSide' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxiliaryQuantitiesHForDriveSide

    @property
    def auxiliary_quantities_h_for_coast_side(self) -> 'float':
        '''float: 'AuxiliaryQuantitiesHForCoastSide' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxiliaryQuantitiesHForCoastSide

    @property
    def auxiliary_quantities_theta_for_drive_side(self) -> 'float':
        '''float: 'AuxiliaryQuantitiesThetaForDriveSide' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxiliaryQuantitiesThetaForDriveSide

    @property
    def auxiliary_quantities_theta_for_coast_side(self) -> 'float':
        '''float: 'AuxiliaryQuantitiesThetaForCoastSide' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxiliaryQuantitiesThetaForCoastSide

    @property
    def tooth_root_chordal_thickness_per_flank_for_generated_gear_drive_flank(self) -> 'float':
        '''float: 'ToothRootChordalThicknessPerFlankForGeneratedGearDriveFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothRootChordalThicknessPerFlankForGeneratedGearDriveFlank

    @property
    def tooth_root_chordal_thickness_per_flank_for_generated_gear_coast_flank(self) -> 'float':
        '''float: 'ToothRootChordalThicknessPerFlankForGeneratedGearCoastFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothRootChordalThicknessPerFlankForGeneratedGearCoastFlank

    @property
    def tooth_root_chordal_thickness_for_generated_gear(self) -> 'float':
        '''float: 'ToothRootChordalThicknessForGeneratedGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothRootChordalThicknessForGeneratedGear

    @property
    def root_fillet_radius_for_generated_gear_drive_flank(self) -> 'float':
        '''float: 'RootFilletRadiusForGeneratedGearDriveFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RootFilletRadiusForGeneratedGearDriveFlank

    @property
    def root_fillet_radius_for_generated_gear_coast_flank(self) -> 'float':
        '''float: 'RootFilletRadiusForGeneratedGearCoastFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RootFilletRadiusForGeneratedGearCoastFlank

    @property
    def bending_moment_arm_for_generated_gear(self) -> 'float':
        '''float: 'BendingMomentArmForGeneratedGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BendingMomentArmForGeneratedGear

    @property
    def load_application_angle_at_tooth_tip_of_virtual_cylindrical_gear_method_b1(self) -> 'float':
        '''float: 'LoadApplicationAngleAtToothTipOfVirtualCylindricalGearMethodB1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadApplicationAngleAtToothTipOfVirtualCylindricalGearMethodB1

    @property
    def normal_pressure_angle_at_tooth_tip(self) -> 'float':
        '''float: 'NormalPressureAngleAtToothTip' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalPressureAngleAtToothTip

    @property
    def auxiliary_angle_for_tooth_form_and_tooth_correction_factor(self) -> 'float':
        '''float: 'AuxiliaryAngleForToothFormAndToothCorrectionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxiliaryAngleForToothFormAndToothCorrectionFactor

    @property
    def tooth_root_chordal_thickness_per_flank_for_non_generated_gear_drive_flank(self) -> 'float':
        '''float: 'ToothRootChordalThicknessPerFlankForNonGeneratedGearDriveFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothRootChordalThicknessPerFlankForNonGeneratedGearDriveFlank

    @property
    def tooth_root_chordal_thickness_per_flank_for_non_generated_gear_coast_flank(self) -> 'float':
        '''float: 'ToothRootChordalThicknessPerFlankForNonGeneratedGearCoastFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothRootChordalThicknessPerFlankForNonGeneratedGearCoastFlank

    @property
    def auxiliary_quantities_e_for_non_generated_gear_drive_flank(self) -> 'float':
        '''float: 'AuxiliaryQuantitiesEForNonGeneratedGearDriveFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxiliaryQuantitiesEForNonGeneratedGearDriveFlank

    @property
    def auxiliary_quantities_e_for_non_generated_gear_coast_flank(self) -> 'float':
        '''float: 'AuxiliaryQuantitiesEForNonGeneratedGearCoastFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxiliaryQuantitiesEForNonGeneratedGearCoastFlank

    @property
    def tooth_root_chordal_thickness_for_non_generated_gear(self) -> 'float':
        '''float: 'ToothRootChordalThicknessForNonGeneratedGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothRootChordalThicknessForNonGeneratedGear

    @property
    def root_fillet_radius_for_non_generated_gear_drive_flank(self) -> 'float':
        '''float: 'RootFilletRadiusForNonGeneratedGearDriveFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RootFilletRadiusForNonGeneratedGearDriveFlank

    @property
    def root_fillet_radius_for_non_generated_gear_coast_flank(self) -> 'float':
        '''float: 'RootFilletRadiusForNonGeneratedGearCoastFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RootFilletRadiusForNonGeneratedGearCoastFlank

    @property
    def bending_moment_arm_for_non_generated_gear(self) -> 'float':
        '''float: 'BendingMomentArmForNonGeneratedGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BendingMomentArmForNonGeneratedGear

    @property
    def tooth_form_factor_for_non_generated_gear(self) -> 'float':
        '''float: 'ToothFormFactorForNonGeneratedGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothFormFactorForNonGeneratedGear

    @property
    def stress_correction_factor(self) -> 'float':
        '''float: 'StressCorrectionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressCorrectionFactor

    @property
    def la(self) -> 'float':
        '''float: 'La' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.La

    @property
    def notch_parameter(self) -> 'float':
        '''float: 'NotchParameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NotchParameter

    @property
    def relative_surface_condition_factor_for_method_b1(self) -> 'float':
        '''float: 'RelativeSurfaceConditionFactorForMethodB1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeSurfaceConditionFactorForMethodB1

    @property
    def relative_surface_condition_factor_for_through_hardened_and_case_hardened_steels_mean_roughness_1_mum(self) -> 'float':
        '''float: 'RelativeSurfaceConditionFactorForThroughHardenedAndCaseHardenedSteelsMeanRoughness1Mum' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeSurfaceConditionFactorForThroughHardenedAndCaseHardenedSteelsMeanRoughness1Mum

    @property
    def relative_surface_condition_factor_for_non_hardened_steels_mean_roughness_1_mum(self) -> 'float':
        '''float: 'RelativeSurfaceConditionFactorForNonHardenedSteelsMeanRoughness1Mum' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeSurfaceConditionFactorForNonHardenedSteelsMeanRoughness1Mum

    @property
    def relative_surface_condition_factor_for_grey_cast_iron_nitrided_and_nitro_carburized_steels_mean_roughness_1_mum(self) -> 'float':
        '''float: 'RelativeSurfaceConditionFactorForGreyCastIronNitridedAndNitroCarburizedSteelsMeanRoughness1Mum' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeSurfaceConditionFactorForGreyCastIronNitridedAndNitroCarburizedSteelsMeanRoughness1Mum

    @property
    def relative_surface_condition_factor_for_through_hardened_and_case_hardened_steels_1_mum_mean_roughness_40_mum(self) -> 'float':
        '''float: 'RelativeSurfaceConditionFactorForThroughHardenedAndCaseHardenedSteels1MumMeanRoughness40Mum' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeSurfaceConditionFactorForThroughHardenedAndCaseHardenedSteels1MumMeanRoughness40Mum

    @property
    def relative_surface_condition_factor_for_non_hardened_steels_1_mum_mean_roughness_40_mum(self) -> 'float':
        '''float: 'RelativeSurfaceConditionFactorForNonHardenedSteels1MumMeanRoughness40Mum' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeSurfaceConditionFactorForNonHardenedSteels1MumMeanRoughness40Mum

    @property
    def relative_surface_condition_factor_for_grey_cast_iron_nitrided_and_nitro_carburized_steels_1_mum_mean_roughness_40_mum(self) -> 'float':
        '''float: 'RelativeSurfaceConditionFactorForGreyCastIronNitridedAndNitroCarburizedSteels1MumMeanRoughness40Mum' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeSurfaceConditionFactorForGreyCastIronNitridedAndNitroCarburizedSteels1MumMeanRoughness40Mum

    @property
    def relative_notch_sensitivity_factor_for_method_b1(self) -> 'float':
        '''float: 'RelativeNotchSensitivityFactorForMethodB1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeNotchSensitivityFactorForMethodB1

    @property
    def relative_stress_drop_in_notch_root(self) -> 'float':
        '''float: 'RelativeStressDropInNotchRoot' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeStressDropInNotchRoot
