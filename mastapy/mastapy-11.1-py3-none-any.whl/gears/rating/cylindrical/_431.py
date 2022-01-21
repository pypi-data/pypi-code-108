'''_431.py

CylindricalMeshSingleFlankRating
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.gears import _287
from mastapy.gears.gear_designs.cylindrical import _1025, _1024
from mastapy.materials import _237
from mastapy.gears.rating.cylindrical import _426, _425, _429
from mastapy.gears.rating import _332
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_MESH_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical', 'CylindricalMeshSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalMeshSingleFlankRating',)


class CylindricalMeshSingleFlankRating(_332.MeshSingleFlankRating):
    '''CylindricalMeshSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_MESH_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalMeshSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def load_case(self) -> 'str':
        '''str: 'LoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadCase

    @property
    def centre_distance(self) -> 'float':
        '''float: 'CentreDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CentreDistance

    @property
    def operating_normal_pressure_angle(self) -> 'float':
        '''float: 'OperatingNormalPressureAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OperatingNormalPressureAngle

    @property
    def effective_face_width(self) -> 'float':
        '''float: 'EffectiveFaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EffectiveFaceWidth

    @property
    def contact_ratio_source(self) -> '_287.ContactRatioDataSource':
        '''ContactRatioDataSource: 'ContactRatioSource' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.ContactRatioSource)
        return constructor.new(_287.ContactRatioDataSource)(value) if value is not None else None

    @property
    def axial_contact_ratio(self) -> 'float':
        '''float: 'AxialContactRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AxialContactRatio

    @property
    def transverse_contact_ratio(self) -> 'float':
        '''float: 'TransverseContactRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseContactRatio

    @property
    def virtual_contact_ratio(self) -> 'float':
        '''float: 'VirtualContactRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VirtualContactRatio

    @property
    def equivalent_misalignment(self) -> 'float':
        '''float: 'EquivalentMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EquivalentMisalignment

    @property
    def duration(self) -> 'float':
        '''float: 'Duration' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Duration

    @property
    def radial_separating_load(self) -> 'float':
        '''float: 'RadialSeparatingLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RadialSeparatingLoad

    @property
    def nominal_radial_load(self) -> 'float':
        '''float: 'NominalRadialLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalRadialLoad

    @property
    def user_specified_coefficient_of_friction_flash_temperature_method(self) -> 'float':
        '''float: 'UserSpecifiedCoefficientOfFrictionFlashTemperatureMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.UserSpecifiedCoefficientOfFrictionFlashTemperatureMethod

    @property
    def coefficient_of_friction_method_flash_temperature_method(self) -> '_1025.ScuffingCoefficientOfFrictionMethods':
        '''ScuffingCoefficientOfFrictionMethods: 'CoefficientOfFrictionMethodFlashTemperatureMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.CoefficientOfFrictionMethodFlashTemperatureMethod)
        return constructor.new(_1025.ScuffingCoefficientOfFrictionMethods)(value) if value is not None else None

    @property
    def sump_temperature(self) -> 'float':
        '''float: 'SumpTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SumpTemperature

    @property
    def nominal_tangential_load(self) -> 'float':
        '''float: 'NominalTangentialLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalTangentialLoad

    @property
    def transmitted_tangential_load(self) -> 'float':
        '''float: 'TransmittedTangentialLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransmittedTangentialLoad

    @property
    def nominal_transverse_load(self) -> 'float':
        '''float: 'NominalTransverseLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalTransverseLoad

    @property
    def nominal_axial_force(self) -> 'float':
        '''float: 'NominalAxialForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalAxialForce

    @property
    def axial_force(self) -> 'float':
        '''float: 'AxialForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AxialForce

    @property
    def tangential_velocity_at_reference_cylinder(self) -> 'float':
        '''float: 'TangentialVelocityAtReferenceCylinder' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TangentialVelocityAtReferenceCylinder

    @property
    def pitch_line_velocity_at_operating_pitch_diameter(self) -> 'float':
        '''float: 'PitchLineVelocityAtOperatingPitchDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PitchLineVelocityAtOperatingPitchDiameter

    @property
    def elasticity_factor(self) -> 'float':
        '''float: 'ElasticityFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ElasticityFactor

    @property
    def maximum_flash_temperature(self) -> 'float':
        '''float: 'MaximumFlashTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumFlashTemperature

    @property
    def maximum_contact_temperature(self) -> 'float':
        '''float: 'MaximumContactTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumContactTemperature

    @property
    def scuffing_temperature(self) -> 'float':
        '''float: 'ScuffingTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ScuffingTemperature

    @property
    def lubricant_dynamic_viscosity_at_tooth_temperature(self) -> 'float':
        '''float: 'LubricantDynamicViscosityAtToothTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LubricantDynamicViscosityAtToothTemperature

    @property
    def dynamic_factor(self) -> 'float':
        '''float: 'DynamicFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DynamicFactor

    @property
    def mean_coefficient_of_friction_calculated_constant_flash_temperature_method(self) -> 'float':
        '''float: 'MeanCoefficientOfFrictionCalculatedConstantFlashTemperatureMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanCoefficientOfFrictionCalculatedConstantFlashTemperatureMethod

    @property
    def mean_coefficient_of_friction_of_maximum_flash_temperature(self) -> 'float':
        '''float: 'MeanCoefficientOfFrictionOfMaximumFlashTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanCoefficientOfFrictionOfMaximumFlashTemperature

    @property
    def gear_ratio(self) -> 'float':
        '''float: 'GearRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearRatio

    @property
    def signed_gear_ratio(self) -> 'float':
        '''float: 'SignedGearRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SignedGearRatio

    @property
    def reduced_modulus_of_elasticity(self) -> 'float':
        '''float: 'ReducedModulusOfElasticity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReducedModulusOfElasticity

    @property
    def welding_structural_factor(self) -> 'float':
        '''float: 'WeldingStructuralFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WeldingStructuralFactor

    @property
    def pinion_roll_angle_at_highest_point_of_single_tooth_contact(self) -> 'float':
        '''float: 'PinionRollAngleAtHighestPointOfSingleToothContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionRollAngleAtHighestPointOfSingleToothContact

    @property
    def active_length_of_the_line_of_action(self) -> 'float':
        '''float: 'ActiveLengthOfTheLineOfAction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ActiveLengthOfTheLineOfAction

    @property
    def slideto_roll_ratio_at_start_of_active_profile(self) -> 'float':
        '''float: 'SlidetoRollRatioAtStartOfActiveProfile' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SlidetoRollRatioAtStartOfActiveProfile

    @property
    def slideto_roll_ratio_at_end_of_active_profile(self) -> 'float':
        '''float: 'SlidetoRollRatioAtEndOfActiveProfile' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SlidetoRollRatioAtEndOfActiveProfile

    @property
    def slideto_roll_ratio_at_pitch_point(self) -> 'float':
        '''float: 'SlidetoRollRatioAtPitchPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SlidetoRollRatioAtPitchPoint

    @property
    def roll_angle_of_maximum_flash_temperature(self) -> 'float':
        '''float: 'RollAngleOfMaximumFlashTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RollAngleOfMaximumFlashTemperature

    @property
    def line_of_action_parameter_of_maximum_flash_temperature(self) -> 'float':
        '''float: 'LineOfActionParameterOfMaximumFlashTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LineOfActionParameterOfMaximumFlashTemperature

    @property
    def load_sharing_factor_of_maximum_flash_temperature(self) -> 'float':
        '''float: 'LoadSharingFactorOfMaximumFlashTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadSharingFactorOfMaximumFlashTemperature

    @property
    def face_load_factor_contact_source(self) -> 'str':
        '''str: 'FaceLoadFactorContactSource' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceLoadFactorContactSource

    @property
    def misalignment_source(self) -> 'str':
        '''str: 'MisalignmentSource' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MisalignmentSource

    @property
    def effective_arithmetic_mean_roughness(self) -> 'float':
        '''float: 'EffectiveArithmeticMeanRoughness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EffectiveArithmeticMeanRoughness

    @property
    def face_load_factor_contact(self) -> 'float':
        '''float: 'FaceLoadFactorContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceLoadFactorContact

    @property
    def minimum_face_load_factor_for_contact_stress(self) -> 'float':
        '''float: 'MinimumFaceLoadFactorForContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumFaceLoadFactorForContactStress

    @property
    def minimum_dynamic_factor_for_wind_turbine_applications(self) -> 'float':
        '''float: 'MinimumDynamicFactorForWindTurbineApplications' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumDynamicFactorForWindTurbineApplications

    @property
    def transverse_load_factor_contact(self) -> 'float':
        '''float: 'TransverseLoadFactorContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseLoadFactorContact

    @property
    def lubrication_detail(self) -> '_237.LubricationDetail':
        '''LubricationDetail: 'LubricationDetail' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_237.LubricationDetail)(self.wrapped.LubricationDetail) if self.wrapped.LubricationDetail is not None else None

    @property
    def sorted_scuffing_results(self) -> '_426.CylindricalGearScuffingResults':
        '''CylindricalGearScuffingResults: 'SortedScuffingResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_426.CylindricalGearScuffingResults)(self.wrapped.SortedScuffingResults) if self.wrapped.SortedScuffingResults is not None else None

    @property
    def sorted_scuffing_results_without_special_values(self) -> '_426.CylindricalGearScuffingResults':
        '''CylindricalGearScuffingResults: 'SortedScuffingResultsWithoutSpecialValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_426.CylindricalGearScuffingResults)(self.wrapped.SortedScuffingResultsWithoutSpecialValues) if self.wrapped.SortedScuffingResultsWithoutSpecialValues is not None else None

    @property
    def rating_settings(self) -> '_425.CylindricalGearRatingSettings':
        '''CylindricalGearRatingSettings: 'RatingSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_425.CylindricalGearRatingSettings)(self.wrapped.RatingSettings) if self.wrapped.RatingSettings is not None else None

    @property
    def scuffing(self) -> '_1024.Scuffing':
        '''Scuffing: 'Scuffing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1024.Scuffing)(self.wrapped.Scuffing) if self.wrapped.Scuffing is not None else None

    @property
    def gear_single_flank_ratings(self) -> 'List[_429.CylindricalGearSingleFlankRating]':
        '''List[CylindricalGearSingleFlankRating]: 'GearSingleFlankRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.GearSingleFlankRatings, constructor.new(_429.CylindricalGearSingleFlankRating))
        return value
