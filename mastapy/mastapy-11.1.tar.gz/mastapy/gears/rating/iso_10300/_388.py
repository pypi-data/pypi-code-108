'''_388.py

ISO10300MeshSingleFlankRating
'''


from typing import Generic, TypeVar

from mastapy._internal import constructor
from mastapy.gears.rating.conical import _506
from mastapy.gears.rating.virtual_cylindrical_gears import _355
from mastapy._internal.python_net import python_net_import

_ISO10300_MESH_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Iso10300', 'ISO10300MeshSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO10300MeshSingleFlankRating',)


T = TypeVar('T', bound='_355.VirtualCylindricalGearBasic')


class ISO10300MeshSingleFlankRating(_506.ConicalMeshSingleFlankRating, Generic[T]):
    '''ISO10300MeshSingleFlankRating

    This is a mastapy class.

    Generic Types:
        T
    '''

    TYPE = _ISO10300_MESH_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO10300MeshSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def rating_standard_name(self) -> 'str':
        '''str: 'RatingStandardName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RatingStandardName

    @property
    def application_factor(self) -> 'float':
        '''float: 'ApplicationFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ApplicationFactor

    @property
    def nominal_tangential_force_of_virtual_cylindrical_gear(self) -> 'float':
        '''float: 'NominalTangentialForceOfVirtualCylindricalGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalTangentialForceOfVirtualCylindricalGear

    @property
    def dynamic_factor(self) -> 'float':
        '''float: 'DynamicFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DynamicFactor

    @property
    def relative_hypoid_offset(self) -> 'float':
        '''float: 'RelativeHypoidOffset' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeHypoidOffset

    @property
    def dimensionless_reference_speed(self) -> 'float':
        '''float: 'DimensionlessReferenceSpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DimensionlessReferenceSpeed

    @property
    def resonance_speed_of_pinion(self) -> 'float':
        '''float: 'ResonanceSpeedOfPinion' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ResonanceSpeedOfPinion

    @property
    def relative_mass_per_unit_face_width(self) -> 'float':
        '''float: 'RelativeMassPerUnitFaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeMassPerUnitFaceWidth

    @property
    def mean_mesh_stiffness(self) -> 'float':
        '''float: 'MeanMeshStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanMeshStiffness

    @property
    def correction_factor_of_tooth_stiffness_for_non_average_conditions(self) -> 'float':
        '''float: 'CorrectionFactorOfToothStiffnessForNonAverageConditions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CorrectionFactorOfToothStiffnessForNonAverageConditions

    @property
    def dynamic_factor_for_method_b(self) -> 'float':
        '''float: 'DynamicFactorForMethodB' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DynamicFactorForMethodB

    @property
    def dynamic_factor_for_method_b_sub_critical_sector(self) -> 'float':
        '''float: 'DynamicFactorForMethodBSubCriticalSector' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DynamicFactorForMethodBSubCriticalSector

    @property
    def factor_for_calculating_the_dynamic_factor_kvb(self) -> 'float':
        '''float: 'FactorForCalculatingTheDynamicFactorKVB' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FactorForCalculatingTheDynamicFactorKVB

    @property
    def effective_pitch_deviation(self) -> 'float':
        '''float: 'EffectivePitchDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EffectivePitchDeviation

    @property
    def single_stiffness(self) -> 'float':
        '''float: 'SingleStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SingleStiffness

    @property
    def dynamic_factor_for_method_b_main_resonance_sector(self) -> 'float':
        '''float: 'DynamicFactorForMethodBMainResonanceSector' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DynamicFactorForMethodBMainResonanceSector

    @property
    def dynamic_factor_for_method_b_super_critical_sector(self) -> 'float':
        '''float: 'DynamicFactorForMethodBSuperCriticalSector' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DynamicFactorForMethodBSuperCriticalSector

    @property
    def dynamic_factor_for_method_b_intermediate_sector(self) -> 'float':
        '''float: 'DynamicFactorForMethodBIntermediateSector' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DynamicFactorForMethodBIntermediateSector

    @property
    def cv_1_dynamic_factor_influence_factor(self) -> 'float':
        '''float: 'Cv1DynamicFactorInfluenceFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Cv1DynamicFactorInfluenceFactor

    @property
    def cv_2_dynamic_factor_influence_factor(self) -> 'float':
        '''float: 'Cv2DynamicFactorInfluenceFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Cv2DynamicFactorInfluenceFactor

    @property
    def cv_3_dynamic_factor_influence_factor(self) -> 'float':
        '''float: 'Cv3DynamicFactorInfluenceFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Cv3DynamicFactorInfluenceFactor

    @property
    def cv_4_dynamic_factor_influence_factor(self) -> 'float':
        '''float: 'Cv4DynamicFactorInfluenceFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Cv4DynamicFactorInfluenceFactor

    @property
    def cv_5_dynamic_factor_influence_factor(self) -> 'float':
        '''float: 'Cv5DynamicFactorInfluenceFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Cv5DynamicFactorInfluenceFactor

    @property
    def cv_6_dynamic_factor_influence_factor(self) -> 'float':
        '''float: 'Cv6DynamicFactorInfluenceFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Cv6DynamicFactorInfluenceFactor

    @property
    def cv_7_dynamic_factor_influence_factor(self) -> 'float':
        '''float: 'Cv7DynamicFactorInfluenceFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Cv7DynamicFactorInfluenceFactor

    @property
    def cv_12_dynamic_factor_influence_factor(self) -> 'float':
        '''float: 'Cv12DynamicFactorInfluenceFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Cv12DynamicFactorInfluenceFactor

    @property
    def cv_56_dynamic_factor_influence_factor(self) -> 'float':
        '''float: 'Cv56DynamicFactorInfluenceFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Cv56DynamicFactorInfluenceFactor

    @property
    def dynamic_factor_for_method_c(self) -> 'float':
        '''float: 'DynamicFactorForMethodC' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DynamicFactorForMethodC

    @property
    def wheel_tangential_speed_at_outer_end_heel_of_the_reference_cone(self) -> 'float':
        '''float: 'WheelTangentialSpeedAtOuterEndHeelOfTheReferenceCone' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelTangentialSpeedAtOuterEndHeelOfTheReferenceCone

    @property
    def auxiliary_factor_a_for_calculating_the_dynamic_factor_kvc(self) -> 'float':
        '''float: 'AuxiliaryFactorAForCalculatingTheDynamicFactorKVC' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxiliaryFactorAForCalculatingTheDynamicFactorKVC

    @property
    def auxiliary_factor_x_for_calculating_the_dynamic_factor_kvc(self) -> 'float':
        '''float: 'AuxiliaryFactorXForCalculatingTheDynamicFactorKVC' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxiliaryFactorXForCalculatingTheDynamicFactorKVC

    @property
    def accuracy_grade_according_to_iso17485(self) -> 'float':
        '''float: 'AccuracyGradeAccordingToISO17485' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AccuracyGradeAccordingToISO17485

    @property
    def max_wheel_tangential_speed_at_outer_end_heel_of_the_reference_cone(self) -> 'float':
        '''float: 'MaxWheelTangentialSpeedAtOuterEndHeelOfTheReferenceCone' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaxWheelTangentialSpeedAtOuterEndHeelOfTheReferenceCone

    @property
    def max_single_pitch_deviation(self) -> 'float':
        '''float: 'MaxSinglePitchDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaxSinglePitchDeviation

    @property
    def running_in_allowance(self) -> 'float':
        '''float: 'RunningInAllowance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RunningInAllowance

    @property
    def wheel_running_in_allowance_for_through_hardened_steels(self) -> 'float':
        '''float: 'WheelRunningInAllowanceForThroughHardenedSteels' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelRunningInAllowanceForThroughHardenedSteels

    @property
    def pinion_running_in_allowance_for_through_hardened_steels(self) -> 'float':
        '''float: 'PinionRunningInAllowanceForThroughHardenedSteels' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionRunningInAllowanceForThroughHardenedSteels

    @property
    def running_in_allowance_for_grey_cast_iron(self) -> 'float':
        '''float: 'RunningInAllowanceForGreyCastIron' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RunningInAllowanceForGreyCastIron

    @property
    def running_in_allowance_for_case_hardened_and_nitrided_gears(self) -> 'float':
        '''float: 'RunningInAllowanceForCaseHardenedAndNitridedGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RunningInAllowanceForCaseHardenedAndNitridedGears

    @property
    def face_load_factor_contact(self) -> 'float':
        '''float: 'FaceLoadFactorContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceLoadFactorContact

    @property
    def face_load_factor_for_method_c_contact(self) -> 'float':
        '''float: 'FaceLoadFactorForMethodCContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceLoadFactorForMethodCContact

    @property
    def face_load_factor_bending(self) -> 'float':
        '''float: 'FaceLoadFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceLoadFactorBending

    @property
    def lengthwise_curvature_factor_for_bending_stress(self) -> 'float':
        '''float: 'LengthwiseCurvatureFactorForBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LengthwiseCurvatureFactorForBendingStress

    @property
    def exponent_in_the_formula_for_lengthwise_curvature_factor(self) -> 'float':
        '''float: 'ExponentInTheFormulaForLengthwiseCurvatureFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ExponentInTheFormulaForLengthwiseCurvatureFactor

    @property
    def lengthwise_tooth_mean_radius_of_curvature(self) -> 'float':
        '''float: 'LengthwiseToothMeanRadiusOfCurvature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LengthwiseToothMeanRadiusOfCurvature

    @property
    def lead_angle_of_face_hobbing_cutter(self) -> 'float':
        '''float: 'LeadAngleOfFaceHobbingCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LeadAngleOfFaceHobbingCutter

    @property
    def eta_1(self) -> 'float':
        '''float: 'Eta1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Eta1

    @property
    def transverse_load_factor_for_contact(self) -> 'float':
        '''float: 'TransverseLoadFactorForContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseLoadFactorForContact

    @property
    def transverse_load_factor_for_bending_stress(self) -> 'float':
        '''float: 'TransverseLoadFactorForBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseLoadFactorForBendingStress

    @property
    def transverse_load_factors_for_bevel_gear_with_virtual_contact_ratio_less_or_equal_to_2(self) -> 'float':
        '''float: 'TransverseLoadFactorsForBevelGearWithVirtualContactRatioLessOrEqualTo2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseLoadFactorsForBevelGearWithVirtualContactRatioLessOrEqualTo2

    @property
    def tangential_force_at_mid_face_width_on_the_pitch_cone(self) -> 'float':
        '''float: 'TangentialForceAtMidFaceWidthOnThePitchCone' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TangentialForceAtMidFaceWidthOnThePitchCone

    @property
    def transverse_load_factor_for_bevel_gear_with_virtual_contact_ratio_greater_than_2(self) -> 'float':
        '''float: 'TransverseLoadFactorForBevelGearWithVirtualContactRatioGreaterThan2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseLoadFactorForBevelGearWithVirtualContactRatioGreaterThan2

    @property
    def preliminary_transverse_load_factor_for_contact_method_b(self) -> 'float':
        '''float: 'PreliminaryTransverseLoadFactorForContactMethodB' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PreliminaryTransverseLoadFactorForContactMethodB

    @property
    def transverse_load_factor_for_bending_stress_method_b(self) -> 'float':
        '''float: 'TransverseLoadFactorForBendingStressMethodB' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseLoadFactorForBendingStressMethodB

    @property
    def preliminary_transverse_load_factor_for_contact_method_c(self) -> 'float':
        '''float: 'PreliminaryTransverseLoadFactorForContactMethodC' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PreliminaryTransverseLoadFactorForContactMethodC

    @property
    def transverse_load_factor_for_bending_stress_method_c(self) -> 'float':
        '''float: 'TransverseLoadFactorForBendingStressMethodC' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseLoadFactorForBendingStressMethodC

    @property
    def elasticity_factor(self) -> 'float':
        '''float: 'ElasticityFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ElasticityFactor

    @property
    def modulus_of_elasticity(self) -> 'float':
        '''float: 'ModulusOfElasticity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ModulusOfElasticity

    @property
    def mean_relative_roughness(self) -> 'float':
        '''float: 'MeanRelativeRoughness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanRelativeRoughness
