'''_481.py

ISO6336AbstractMetalMeshSingleFlankRating
'''


from typing import List

from mastapy.gears.rating.cylindrical import (
    _438, _442, _443, _422
)
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.gears.gear_designs.cylindrical import _1027
from mastapy.gears.rating.cylindrical.iso6336 import (
    _475, _477, _480, _479
)
from mastapy._internal.cast_exception import CastException
from mastapy._internal.python_net import python_net_import

_ISO6336_ABSTRACT_METAL_MESH_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.ISO6336', 'ISO6336AbstractMetalMeshSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO6336AbstractMetalMeshSingleFlankRating',)


class ISO6336AbstractMetalMeshSingleFlankRating(_479.ISO6336AbstractMeshSingleFlankRating):
    '''ISO6336AbstractMetalMeshSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _ISO6336_ABSTRACT_METAL_MESH_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO6336AbstractMetalMeshSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def micropitting_rating_method(self) -> '_438.MicropittingRatingMethod':
        '''MicropittingRatingMethod: 'MicropittingRatingMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.MicropittingRatingMethod)
        return constructor.new(_438.MicropittingRatingMethod)(value) if value is not None else None

    @property
    def scuffing_rating_method_flash_temperature_method(self) -> '_442.ScuffingFlashTemperatureRatingMethod':
        '''ScuffingFlashTemperatureRatingMethod: 'ScuffingRatingMethodFlashTemperatureMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.ScuffingRatingMethodFlashTemperatureMethod)
        return constructor.new(_442.ScuffingFlashTemperatureRatingMethod)(value) if value is not None else None

    @property
    def scuffing_rating_method_integral_temperature_method(self) -> '_443.ScuffingIntegralTemperatureRatingMethod':
        '''ScuffingIntegralTemperatureRatingMethod: 'ScuffingRatingMethodIntegralTemperatureMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.ScuffingRatingMethodIntegralTemperatureMethod)
        return constructor.new(_443.ScuffingIntegralTemperatureRatingMethod)(value) if value is not None else None

    @property
    def equivalent_misalignment_due_to_system_deflection(self) -> 'float':
        '''float: 'EquivalentMisalignmentDueToSystemDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EquivalentMisalignmentDueToSystemDeflection

    @property
    def tip_relief(self) -> 'float':
        '''float: 'TipRelief' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipRelief

    @property
    def drive_gear_tip_relief(self) -> 'float':
        '''float: 'DriveGearTipRelief' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DriveGearTipRelief

    @property
    def single_stiffness(self) -> 'float':
        '''float: 'SingleStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SingleStiffness

    @property
    def stiffness_material_factor(self) -> 'float':
        '''float: 'StiffnessMaterialFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessMaterialFactor

    @property
    def mesh_stiffness(self) -> 'float':
        '''float: 'MeshStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeshStiffness

    @property
    def effective_equivalent_misalignment(self) -> 'float':
        '''float: 'EffectiveEquivalentMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EffectiveEquivalentMisalignment

    @property
    def running_in_allowance_equivalent_misalignment(self) -> 'float':
        '''float: 'RunningInAllowanceEquivalentMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RunningInAllowanceEquivalentMisalignment

    @property
    def theoretical_single_stiffness(self) -> 'float':
        '''float: 'TheoreticalSingleStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TheoreticalSingleStiffness

    @property
    def tooth_stiffness_correction_factor(self) -> 'float':
        '''float: 'ToothStiffnessCorrectionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothStiffnessCorrectionFactor

    @property
    def gear_blank_factor(self) -> 'float':
        '''float: 'GearBlankFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearBlankFactor

    @property
    def basic_rack_factor(self) -> 'float':
        '''float: 'BasicRackFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicRackFactor

    @property
    def dynamic_factor_source(self) -> 'str':
        '''str: 'DynamicFactorSource' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DynamicFactorSource

    @property
    def transverse_base_pitch_deviation_factor_for_the_dynamic_load(self) -> 'float':
        '''float: 'TransverseBasePitchDeviationFactorForTheDynamicLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseBasePitchDeviationFactorForTheDynamicLoad

    @property
    def profile_form_deviation_factor_for_the_dynamic_load(self) -> 'float':
        '''float: 'ProfileFormDeviationFactorForTheDynamicLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProfileFormDeviationFactorForTheDynamicLoad

    @property
    def micro_geometry_factor_for_the_dynamic_load(self) -> 'float':
        '''float: 'MicroGeometryFactorForTheDynamicLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MicroGeometryFactorForTheDynamicLoad

    @property
    def resonance_ratio(self) -> 'float':
        '''float: 'ResonanceRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ResonanceRatio

    @property
    def resonance_speed(self) -> 'float':
        '''float: 'ResonanceSpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ResonanceSpeed

    @property
    def effective_transverse_base_pitch_deviation(self) -> 'float':
        '''float: 'EffectiveTransverseBasePitchDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EffectiveTransverseBasePitchDeviation

    @property
    def effective_profile_form_deviation(self) -> 'float':
        '''float: 'EffectiveProfileFormDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EffectiveProfileFormDeviation

    @property
    def relative_mass_per_unit_face_width(self) -> 'float':
        '''float: 'RelativeMassPerUnitFaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeMassPerUnitFaceWidth

    @property
    def resonance_ratio_in_the_main_resonance_range(self) -> 'float':
        '''float: 'ResonanceRatioInTheMainResonanceRange' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ResonanceRatioInTheMainResonanceRange

    @property
    def running_in(self) -> 'float':
        '''float: 'RunningIn' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RunningIn

    @property
    def running_in_profile_form_deviation(self) -> 'float':
        '''float: 'RunningInProfileFormDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RunningInProfileFormDeviation

    @property
    def face_load_factor_contact_source(self) -> 'str':
        '''str: 'FaceLoadFactorContactSource' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceLoadFactorContactSource

    @property
    def face_load_factor_bending(self) -> 'float':
        '''float: 'FaceLoadFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceLoadFactorBending

    @property
    def maximum_base_pitch_deviation(self) -> 'float':
        '''float: 'MaximumBasePitchDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumBasePitchDeviation

    @property
    def maximum_profile_form_deviation(self) -> 'float':
        '''float: 'MaximumProfileFormDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumProfileFormDeviation

    @property
    def transverse_load_factor_contact(self) -> 'float':
        '''float: 'TransverseLoadFactorContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseLoadFactorContact

    @property
    def initial_equivalent_misalignment(self) -> 'float':
        '''float: 'InitialEquivalentMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InitialEquivalentMisalignment

    @property
    def allowable_stress_number_contact(self) -> 'float':
        '''float: 'AllowableStressNumberContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableStressNumberContact

    @property
    def tip_relief_calculated(self) -> 'float':
        '''float: 'TipReliefCalculated' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipReliefCalculated

    @property
    def misalignment_due_to_micro_geometry_lead_relief(self) -> 'float':
        '''float: 'MisalignmentDueToMicroGeometryLeadRelief' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MisalignmentDueToMicroGeometryLeadRelief

    @property
    def mesh_misalignment_due_to_manufacturing_deviations(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MeshMisalignmentDueToManufacturingDeviations' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MeshMisalignmentDueToManufacturingDeviations) if self.wrapped.MeshMisalignmentDueToManufacturingDeviations is not None else None

    @property
    def maximum_contact_temperature(self) -> 'float':
        '''float: 'MaximumContactTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumContactTemperature

    @property
    def scuffing_safety_factor_flash_temperature_method(self) -> 'float':
        '''float: 'ScuffingSafetyFactorFlashTemperatureMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ScuffingSafetyFactorFlashTemperatureMethod

    @property
    def maximum_flash_temperature(self) -> 'float':
        '''float: 'MaximumFlashTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumFlashTemperature

    @property
    def bulk_tooth_temperature_flash_temperature_method(self) -> 'float':
        '''float: 'BulkToothTemperatureFlashTemperatureMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BulkToothTemperatureFlashTemperatureMethod

    @property
    def average_flash_temperature(self) -> 'float':
        '''float: 'AverageFlashTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageFlashTemperature

    @property
    def scuffing_temperature_method(self) -> '_1027.ScuffingTemperatureMethodsISO':
        '''ScuffingTemperatureMethodsISO: 'ScuffingTemperatureMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.ScuffingTemperatureMethod)
        return constructor.new(_1027.ScuffingTemperatureMethodsISO)(value) if value is not None else None

    @property
    def user_input_scuffing_temperature_for_long_contact_times(self) -> 'float':
        '''float: 'UserInputScuffingTemperatureForLongContactTimes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.UserInputScuffingTemperatureForLongContactTimes

    @property
    def user_input_scuffing_integral_temperature_for_long_contact_times(self) -> 'float':
        '''float: 'UserInputScuffingIntegralTemperatureForLongContactTimes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.UserInputScuffingIntegralTemperatureForLongContactTimes

    @property
    def scuffing_temperature_gradient(self) -> 'float':
        '''float: 'ScuffingTemperatureGradient' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ScuffingTemperatureGradient

    @property
    def scuffing_temperature_gradient_integral(self) -> 'float':
        '''float: 'ScuffingTemperatureGradientIntegral' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ScuffingTemperatureGradientIntegral

    @property
    def contact_exposure_time_flash_temperature_method(self) -> 'float':
        '''float: 'ContactExposureTimeFlashTemperatureMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactExposureTimeFlashTemperatureMethod

    @property
    def contact_exposure_time_integral_temperature_method(self) -> 'float':
        '''float: 'ContactExposureTimeIntegralTemperatureMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactExposureTimeIntegralTemperatureMethod

    @property
    def longest_contact_exposure_time(self) -> 'float':
        '''float: 'LongestContactExposureTime' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LongestContactExposureTime

    @property
    def longest_contact_exposure_time_integral(self) -> 'float':
        '''float: 'LongestContactExposureTimeIntegral' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LongestContactExposureTimeIntegral

    @property
    def scuffing_temperature_at_medium_velocity(self) -> 'float':
        '''float: 'ScuffingTemperatureAtMediumVelocity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ScuffingTemperatureAtMediumVelocity

    @property
    def scuffing_temperature_at_high_velocity(self) -> 'float':
        '''float: 'ScuffingTemperatureAtHighVelocity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ScuffingTemperatureAtHighVelocity

    @property
    def contact_time_at_medium_velocity(self) -> 'float':
        '''float: 'ContactTimeAtMediumVelocity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactTimeAtMediumVelocity

    @property
    def contact_time_at_high_velocity(self) -> 'float':
        '''float: 'ContactTimeAtHighVelocity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactTimeAtHighVelocity

    @property
    def scuffing_temperature(self) -> 'float':
        '''float: 'ScuffingTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ScuffingTemperature

    @property
    def lubrication_system_factor(self) -> 'float':
        '''float: 'LubricationSystemFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LubricationSystemFactor

    @property
    def optimal_tip_relief(self) -> 'float':
        '''float: 'OptimalTipRelief' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OptimalTipRelief

    @property
    def effective_tip_relief(self) -> 'float':
        '''float: 'EffectiveTipRelief' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EffectiveTipRelief

    @property
    def equivalent_tip_relief_of_pinion(self) -> 'float':
        '''float: 'EquivalentTipReliefOfPinion' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EquivalentTipReliefOfPinion

    @property
    def equivalent_tip_relief_of_wheel(self) -> 'float':
        '''float: 'EquivalentTipReliefOfWheel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EquivalentTipReliefOfWheel

    @property
    def approach_factor_of_maximum_flash_temperature(self) -> 'float':
        '''float: 'ApproachFactorOfMaximumFlashTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ApproachFactorOfMaximumFlashTemperature

    @property
    def thermo_elastic_factor_of_maximum_flash_temperature(self) -> 'float':
        '''float: 'ThermoElasticFactorOfMaximumFlashTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ThermoElasticFactorOfMaximumFlashTemperature

    @property
    def angle_factor(self) -> 'float':
        '''float: 'AngleFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AngleFactor

    @property
    def multiple_path_factor(self) -> 'float':
        '''float: 'MultiplePathFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MultiplePathFactor

    @property
    def transverse_unit_load(self) -> 'float':
        '''float: 'TransverseUnitLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseUnitLoad

    @property
    def normal_unit_load(self) -> 'float':
        '''float: 'NormalUnitLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalUnitLoad

    @property
    def mean_coefficient_of_friction_calculated_constant_flash_temperature_method(self) -> 'float':
        '''float: 'MeanCoefficientOfFrictionCalculatedConstantFlashTemperatureMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanCoefficientOfFrictionCalculatedConstantFlashTemperatureMethod

    @property
    def lubricant_factor_integral(self) -> 'float':
        '''float: 'LubricantFactorIntegral' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LubricantFactorIntegral

    @property
    def lubricant_factor_flash(self) -> 'float':
        '''float: 'LubricantFactorFlash' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LubricantFactorFlash

    @property
    def lubricant_density_at_bulk_tooth_temperature(self) -> 'float':
        '''float: 'LubricantDensityAtBulkToothTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LubricantDensityAtBulkToothTemperature

    @property
    def lubricant_density_at_micropitting_bulk_tooth_temperature(self) -> 'float':
        '''float: 'LubricantDensityAtMicropittingBulkToothTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LubricantDensityAtMicropittingBulkToothTemperature

    @property
    def lubricant_density_at_156_degrees_celsius(self) -> 'float':
        '''float: 'LubricantDensityAt156DegreesCelsius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LubricantDensityAt156DegreesCelsius

    @property
    def mean_coefficient_of_friction_integral_temperature_method(self) -> 'float':
        '''float: 'MeanCoefficientOfFrictionIntegralTemperatureMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanCoefficientOfFrictionIntegralTemperatureMethod

    @property
    def normal_relative_radius_of_curvature_at_pitch_point_integral_temperature_method(self) -> 'float':
        '''float: 'NormalRelativeRadiusOfCurvatureAtPitchPointIntegralTemperatureMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalRelativeRadiusOfCurvatureAtPitchPointIntegralTemperatureMethod

    @property
    def helical_load_factor(self) -> 'float':
        '''float: 'HelicalLoadFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HelicalLoadFactor

    @property
    def run_in_grade(self) -> 'int':
        '''int: 'RunInGrade' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RunInGrade

    @property
    def run_in_factor(self) -> 'float':
        '''float: 'RunInFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RunInFactor

    @property
    def bulk_tooth_temperature_integral_temperature_method(self) -> 'float':
        '''float: 'BulkToothTemperatureIntegralTemperatureMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BulkToothTemperatureIntegralTemperatureMethod

    @property
    def mean_flash_temperature(self) -> 'float':
        '''float: 'MeanFlashTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanFlashTemperature

    @property
    def contact_ratio_factor(self) -> 'float':
        '''float: 'ContactRatioFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactRatioFactor

    @property
    def basic_mean_flash_temperature(self) -> 'float':
        '''float: 'BasicMeanFlashTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicMeanFlashTemperature

    @property
    def geometry_factor_at_pinion_tooth_tip(self) -> 'float':
        '''float: 'GeometryFactorAtPinionToothTip' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GeometryFactorAtPinionToothTip

    @property
    def approach_factor_integral(self) -> 'float':
        '''float: 'ApproachFactorIntegral' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ApproachFactorIntegral

    @property
    def tip_relief_factor_integral(self) -> 'float':
        '''float: 'TipReliefFactorIntegral' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipReliefFactorIntegral

    @property
    def integral_contact_temperature(self) -> 'float':
        '''float: 'IntegralContactTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IntegralContactTemperature

    @property
    def integral_scuffing_temperature(self) -> 'float':
        '''float: 'IntegralScuffingTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IntegralScuffingTemperature

    @property
    def relative_welding_factor(self) -> 'float':
        '''float: 'RelativeWeldingFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeWeldingFactor

    @property
    def user_input_scuffing_temperature(self) -> 'float':
        '''float: 'UserInputScuffingTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.UserInputScuffingTemperature

    @property
    def scuffing_safety_factor_integral_temperature_method(self) -> 'float':
        '''float: 'ScuffingSafetyFactorIntegralTemperatureMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ScuffingSafetyFactorIntegralTemperatureMethod

    @property
    def scuffing_load_safety_factor_integral_temperature_method(self) -> 'float':
        '''float: 'ScuffingLoadSafetyFactorIntegralTemperatureMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ScuffingLoadSafetyFactorIntegralTemperatureMethod

    @property
    def micropitting_safety_factor(self) -> 'float':
        '''float: 'MicropittingSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MicropittingSafetyFactor

    @property
    def permissible_specific_lubricant_film_thickness_from_figure_a1(self) -> 'float':
        '''float: 'PermissibleSpecificLubricantFilmThicknessFromFigureA1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleSpecificLubricantFilmThicknessFromFigureA1

    @property
    def permissible_specific_lubricant_film_thickness(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'PermissibleSpecificLubricantFilmThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.PermissibleSpecificLubricantFilmThickness) if self.wrapped.PermissibleSpecificLubricantFilmThickness is not None else None

    @property
    def test_torque(self) -> 'float':
        '''float: 'TestTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TestTorque

    @property
    def limiting_specific_lubricant_film_thickness_of_the_test_gears(self) -> 'float':
        '''float: 'LimitingSpecificLubricantFilmThicknessOfTheTestGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LimitingSpecificLubricantFilmThicknessOfTheTestGears

    @property
    def minimum_specific_lubricant_film_thickness_in_the_contact_area(self) -> 'float':
        '''float: 'MinimumSpecificLubricantFilmThicknessInTheContactArea' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumSpecificLubricantFilmThicknessInTheContactArea

    @property
    def minimum_lubricant_film_thickness(self) -> 'float':
        '''float: 'MinimumLubricantFilmThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumLubricantFilmThickness

    @property
    def material_factor(self) -> 'float':
        '''float: 'MaterialFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaterialFactor

    @property
    def material_parameter(self) -> 'float':
        '''float: 'MaterialParameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaterialParameter

    @property
    def pressure_viscosity_coefficient_at_bulk_temperature(self) -> 'float':
        '''float: 'PressureViscosityCoefficientAtBulkTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PressureViscosityCoefficientAtBulkTemperature

    @property
    def pressure_viscosity_coefficient_at_38_degrees_c(self) -> 'float':
        '''float: 'PressureViscosityCoefficientAt38DegreesC' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PressureViscosityCoefficientAt38DegreesC

    @property
    def lubricant_dynamic_viscosity_at_tooth_temperature_micropitting(self) -> 'float':
        '''float: 'LubricantDynamicViscosityAtToothTemperatureMicropitting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LubricantDynamicViscosityAtToothTemperatureMicropitting

    @property
    def length_of_path_of_contact(self) -> 'float':
        '''float: 'LengthOfPathOfContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LengthOfPathOfContact

    @property
    def highest_local_contact_temperature(self) -> 'float':
        '''float: 'HighestLocalContactTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HighestLocalContactTemperature

    @property
    def bulk_temperature_for_micropitting(self) -> 'float':
        '''float: 'BulkTemperatureForMicropitting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BulkTemperatureForMicropitting

    @property
    def tip_relief_factor_for_micropitting(self) -> 'float':
        '''float: 'TipReliefFactorForMicropitting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipReliefFactorForMicropitting

    @property
    def load_losses_factor(self) -> 'float':
        '''float: 'LoadLossesFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadLossesFactor

    @property
    def roughness_factor_micropitting(self) -> 'float':
        '''float: 'RoughnessFactorMicropitting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RoughnessFactorMicropitting

    @property
    def local_hertzian_contact_stress_calculation_method(self) -> 'str':
        '''str: 'LocalHertzianContactStressCalculationMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LocalHertzianContactStressCalculationMethod

    @property
    def sorted_micro_pitting_results(self) -> '_422.CylindricalGearMicroPittingResults':
        '''CylindricalGearMicroPittingResults: 'SortedMicroPittingResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_422.CylindricalGearMicroPittingResults)(self.wrapped.SortedMicroPittingResults) if self.wrapped.SortedMicroPittingResults is not None else None

    @property
    def single_flank_rating_of_test_gears_for_micropitting(self) -> '_475.ISO63362006MeshSingleFlankRating':
        '''ISO63362006MeshSingleFlankRating: 'SingleFlankRatingOfTestGearsForMicropitting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _475.ISO63362006MeshSingleFlankRating.TYPE not in self.wrapped.SingleFlankRatingOfTestGearsForMicropitting.__class__.__mro__:
            raise CastException('Failed to cast single_flank_rating_of_test_gears_for_micropitting to ISO63362006MeshSingleFlankRating. Expected: {}.'.format(self.wrapped.SingleFlankRatingOfTestGearsForMicropitting.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SingleFlankRatingOfTestGearsForMicropitting.__class__)(self.wrapped.SingleFlankRatingOfTestGearsForMicropitting) if self.wrapped.SingleFlankRatingOfTestGearsForMicropitting is not None else None

    @property
    def isodin_cylindrical_gear_single_flank_ratings(self) -> 'List[_480.ISO6336AbstractMetalGearSingleFlankRating]':
        '''List[ISO6336AbstractMetalGearSingleFlankRating]: 'ISODINCylindricalGearSingleFlankRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ISODINCylindricalGearSingleFlankRatings, constructor.new(_480.ISO6336AbstractMetalGearSingleFlankRating))
        return value
