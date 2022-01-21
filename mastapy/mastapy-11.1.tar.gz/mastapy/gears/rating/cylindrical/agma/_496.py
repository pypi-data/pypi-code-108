'''_496.py

AGMA2101MeshSingleFlankRating
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.gears.gear_designs.cylindrical import _983, _1026
from mastapy.materials import _225
from mastapy.gears.rating.cylindrical.agma import _495
from mastapy.gears.rating.cylindrical import _431
from mastapy._internal.python_net import python_net_import

_AGMA2101_MESH_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.AGMA', 'AGMA2101MeshSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMA2101MeshSingleFlankRating',)


class AGMA2101MeshSingleFlankRating(_431.CylindricalMeshSingleFlankRating):
    '''AGMA2101MeshSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _AGMA2101_MESH_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMA2101MeshSingleFlankRating.TYPE'):
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
    def pinion_offset_from_bearing(self) -> 'float':
        '''float: 'PinionOffsetFromBearing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionOffsetFromBearing

    @property
    def bearing_span(self) -> 'float':
        '''float: 'BearingSpan' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BearingSpan

    @property
    def improved_gearing(self) -> 'bool':
        '''bool: 'ImprovedGearing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ImprovedGearing

    @property
    def profile_modification(self) -> '_983.CylindricalGearProfileModifications':
        '''CylindricalGearProfileModifications: 'ProfileModification' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.ProfileModification)
        return constructor.new(_983.CylindricalGearProfileModifications)(value) if value is not None else None

    @property
    def gearing_type(self) -> '_225.GearingTypes':
        '''GearingTypes: 'GearingType' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.GearingType)
        return constructor.new(_225.GearingTypes)(value) if value is not None else None

    @property
    def scuffing_temperature_method(self) -> '_1026.ScuffingTemperatureMethodsAGMA':
        '''ScuffingTemperatureMethodsAGMA: 'ScuffingTemperatureMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.ScuffingTemperatureMethod)
        return constructor.new(_1026.ScuffingTemperatureMethodsAGMA)(value) if value is not None else None

    @property
    def overload_factor(self) -> 'float':
        '''float: 'OverloadFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OverloadFactor

    @property
    def surface_condition_factor(self) -> 'float':
        '''float: 'SurfaceConditionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfaceConditionFactor

    @property
    def parameter_for_calculating_tooth_temperature(self) -> 'float':
        '''float: 'ParameterForCalculatingToothTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ParameterForCalculatingToothTemperature

    @property
    def filter_cutoff_wave_length(self) -> 'float':
        '''float: 'FilterCutoffWaveLength' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FilterCutoffWaveLength

    @property
    def transverse_metric_module(self) -> 'float':
        '''float: 'TransverseMetricModule' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseMetricModule

    @property
    def size_factor_bending(self) -> 'float':
        '''float: 'SizeFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SizeFactorBending

    @property
    def temperature_factor(self) -> 'float':
        '''float: 'TemperatureFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TemperatureFactor

    @property
    def load_distribution_factor(self) -> 'float':
        '''float: 'LoadDistributionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadDistributionFactor

    @property
    def transverse_load_distribution_factor(self) -> 'float':
        '''float: 'TransverseLoadDistributionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseLoadDistributionFactor

    @property
    def load_distribution_factor_source(self) -> 'str':
        '''str: 'LoadDistributionFactorSource' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadDistributionFactorSource

    @property
    def transmission_accuracy_number(self) -> 'float':
        '''float: 'TransmissionAccuracyNumber' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransmissionAccuracyNumber

    @property
    def contact_load_factor(self) -> 'float':
        '''float: 'ContactLoadFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactLoadFactor

    @property
    def operating_centre_distance(self) -> 'float':
        '''float: 'OperatingCentreDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OperatingCentreDistance

    @property
    def sixth_distance_along_line_of_action(self) -> 'float':
        '''float: 'SixthDistanceAlongLineOfAction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SixthDistanceAlongLineOfAction

    @property
    def first_distance_along_line_of_action(self) -> 'float':
        '''float: 'FirstDistanceAlongLineOfAction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FirstDistanceAlongLineOfAction

    @property
    def third_distance_along_line_of_action(self) -> 'float':
        '''float: 'ThirdDistanceAlongLineOfAction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ThirdDistanceAlongLineOfAction

    @property
    def fourth_distance_along_line_of_action(self) -> 'float':
        '''float: 'FourthDistanceAlongLineOfAction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FourthDistanceAlongLineOfAction

    @property
    def fifth_distance_along_line_of_action(self) -> 'float':
        '''float: 'FifthDistanceAlongLineOfAction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FifthDistanceAlongLineOfAction

    @property
    def second_distance_along_line_of_action(self) -> 'float':
        '''float: 'SecondDistanceAlongLineOfAction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SecondDistanceAlongLineOfAction

    @property
    def active_length_of_line_of_contact(self) -> 'float':
        '''float: 'ActiveLengthOfLineOfContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ActiveLengthOfLineOfContact

    @property
    def minimum_contact_length(self) -> 'float':
        '''float: 'MinimumContactLength' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumContactLength

    @property
    def minimum_length_of_contact_lines_per_unit_module(self) -> 'float':
        '''float: 'MinimumLengthOfContactLinesPerUnitModule' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumLengthOfContactLinesPerUnitModule

    @property
    def load_sharing_ratio(self) -> 'float':
        '''float: 'LoadSharingRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadSharingRatio

    @property
    def helical_overlap_factor(self) -> 'float':
        '''float: 'HelicalOverlapFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HelicalOverlapFactor

    @property
    def geometry_factor_i(self) -> 'float':
        '''float: 'GeometryFactorI' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GeometryFactorI

    @property
    def elastic_coefficient(self) -> 'float':
        '''float: 'ElasticCoefficient' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ElasticCoefficient

    @property
    def face_load_distribution_factor(self) -> 'float':
        '''float: 'FaceLoadDistributionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceLoadDistributionFactor

    @property
    def lead_correction_factor(self) -> 'float':
        '''float: 'LeadCorrectionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LeadCorrectionFactor

    @property
    def pinion_proportion_factor(self) -> 'float':
        '''float: 'PinionProportionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionProportionFactor

    @property
    def pinion_proportion_modifier(self) -> 'float':
        '''float: 'PinionProportionModifier' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionProportionModifier

    @property
    def mesh_alignment_factor(self) -> 'float':
        '''float: 'MeshAlignmentFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeshAlignmentFactor

    @property
    def mesh_alignment_correction_factor(self) -> 'float':
        '''float: 'MeshAlignmentCorrectionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeshAlignmentCorrectionFactor

    @property
    def average_roughness_ra(self) -> 'float':
        '''float: 'AverageRoughnessRa' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageRoughnessRa

    @property
    def surface_roughness_constant(self) -> 'float':
        '''float: 'SurfaceRoughnessConstant' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfaceRoughnessConstant

    @property
    def mean_coefficient_of_friction_calculated_constant_flash_temperature_method(self) -> 'float':
        '''float: 'MeanCoefficientOfFrictionCalculatedConstantFlashTemperatureMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanCoefficientOfFrictionCalculatedConstantFlashTemperatureMethod

    @property
    def composite_surface_roughness_at_fc(self) -> 'float':
        '''float: 'CompositeSurfaceRoughnessAtFC' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CompositeSurfaceRoughnessAtFC

    @property
    def combined_derating_factor(self) -> 'float':
        '''float: 'CombinedDeratingFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CombinedDeratingFactor

    @property
    def actual_tangential_load(self) -> 'float':
        '''float: 'ActualTangentialLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ActualTangentialLoad

    @property
    def normal_operating_load(self) -> 'float':
        '''float: 'NormalOperatingLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalOperatingLoad

    @property
    def normal_unit_load(self) -> 'float':
        '''float: 'NormalUnitLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalUnitLoad

    @property
    def sliding_velocity_at_start_of_active_profile(self) -> 'float':
        '''float: 'SlidingVelocityAtStartOfActiveProfile' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SlidingVelocityAtStartOfActiveProfile

    @property
    def sliding_velocity_at_end_of_active_profile(self) -> 'float':
        '''float: 'SlidingVelocityAtEndOfActiveProfile' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SlidingVelocityAtEndOfActiveProfile

    @property
    def sliding_velocity_at_pitch_point(self) -> 'float':
        '''float: 'SlidingVelocityAtPitchPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SlidingVelocityAtPitchPoint

    @property
    def entraining_velocity_at_start_of_active_profile(self) -> 'float':
        '''float: 'EntrainingVelocityAtStartOfActiveProfile' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EntrainingVelocityAtStartOfActiveProfile

    @property
    def entraining_velocity_at_end_of_active_profile(self) -> 'float':
        '''float: 'EntrainingVelocityAtEndOfActiveProfile' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EntrainingVelocityAtEndOfActiveProfile

    @property
    def entraining_velocity_at_pitch_point(self) -> 'float':
        '''float: 'EntrainingVelocityAtPitchPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EntrainingVelocityAtPitchPoint

    @property
    def materials_parameter(self) -> 'float':
        '''float: 'MaterialsParameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaterialsParameter

    @property
    def pressure_viscosity_coefficient(self) -> 'float':
        '''float: 'PressureViscosityCoefficient' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PressureViscosityCoefficient

    @property
    def maximum_contact_temperature(self) -> 'float':
        '''float: 'MaximumContactTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumContactTemperature

    @property
    def maximum_flash_temperature(self) -> 'float':
        '''float: 'MaximumFlashTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumFlashTemperature

    @property
    def tooth_temperature(self) -> 'float':
        '''float: 'ToothTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothTemperature

    @property
    def scuffing_temperature(self) -> 'float':
        '''float: 'ScuffingTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ScuffingTemperature

    @property
    def sump_temperature(self) -> 'float':
        '''float: 'SumpTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SumpTemperature

    @property
    def minimum_film_thickness(self) -> 'float':
        '''float: 'MinimumFilmThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumFilmThickness

    @property
    def minimum_specific_film_thickness(self) -> 'float':
        '''float: 'MinimumSpecificFilmThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumSpecificFilmThickness

    @property
    def probability_of_scuffing(self) -> 'float':
        '''float: 'ProbabilityOfScuffing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProbabilityOfScuffing

    @property
    def probability_of_wear(self) -> 'float':
        '''float: 'ProbabilityOfWear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProbabilityOfWear

    @property
    def gear_single_flank_ratings(self) -> 'List[_495.AGMA2101GearSingleFlankRating]':
        '''List[AGMA2101GearSingleFlankRating]: 'GearSingleFlankRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.GearSingleFlankRatings, constructor.new(_495.AGMA2101GearSingleFlankRating))
        return value

    @property
    def agma_cylindrical_gear_single_flank_ratings(self) -> 'List[_495.AGMA2101GearSingleFlankRating]':
        '''List[AGMA2101GearSingleFlankRating]: 'AGMACylindricalGearSingleFlankRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AGMACylindricalGearSingleFlankRatings, constructor.new(_495.AGMA2101GearSingleFlankRating))
        return value
