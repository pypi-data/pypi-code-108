'''_425.py

CylindricalGearRatingSettings
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.gears.rating.cylindrical import (
    _447, _434, _435, _444,
    _438, _442, _443, _441,
    _448
)
from mastapy._internal.implicit import enum_with_selected_value, overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.materials import _221
from mastapy.utility import _1387
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_RATING_SETTINGS = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical', 'CylindricalGearRatingSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearRatingSettings',)


class CylindricalGearRatingSettings(_1387.PerMachineSettings):
    '''CylindricalGearRatingSettings

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_RATING_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearRatingSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def show_rating_settings_in_report(self) -> 'bool':
        '''bool: 'ShowRatingSettingsInReport' is the original name of this property.'''

        return self.wrapped.ShowRatingSettingsInReport

    @show_rating_settings_in_report.setter
    def show_rating_settings_in_report(self, value: 'bool'):
        self.wrapped.ShowRatingSettingsInReport = bool(value) if value else False

    @property
    def number_of_rotations_for_basic_ltca(self) -> 'int':
        '''int: 'NumberOfRotationsForBasicLTCA' is the original name of this property.'''

        return self.wrapped.NumberOfRotationsForBasicLTCA

    @number_of_rotations_for_basic_ltca.setter
    def number_of_rotations_for_basic_ltca(self, value: 'int'):
        self.wrapped.NumberOfRotationsForBasicLTCA = int(value) if value else 0

    @property
    def number_of_load_strips_for_basic_ltca(self) -> 'int':
        '''int: 'NumberOfLoadStripsForBasicLTCA' is the original name of this property.'''

        return self.wrapped.NumberOfLoadStripsForBasicLTCA

    @number_of_load_strips_for_basic_ltca.setter
    def number_of_load_strips_for_basic_ltca(self, value: 'int'):
        self.wrapped.NumberOfLoadStripsForBasicLTCA = int(value) if value else 0

    @property
    def number_of_points_along_profile_for_scuffing_calculation(self) -> 'int':
        '''int: 'NumberOfPointsAlongProfileForScuffingCalculation' is the original name of this property.'''

        return self.wrapped.NumberOfPointsAlongProfileForScuffingCalculation

    @number_of_points_along_profile_for_scuffing_calculation.setter
    def number_of_points_along_profile_for_scuffing_calculation(self, value: 'int'):
        self.wrapped.NumberOfPointsAlongProfileForScuffingCalculation = int(value) if value else 0

    @property
    def number_of_points_along_profile_for_micropitting_calculation(self) -> 'int':
        '''int: 'NumberOfPointsAlongProfileForMicropittingCalculation' is the original name of this property.'''

        return self.wrapped.NumberOfPointsAlongProfileForMicropittingCalculation

    @number_of_points_along_profile_for_micropitting_calculation.setter
    def number_of_points_along_profile_for_micropitting_calculation(self, value: 'int'):
        self.wrapped.NumberOfPointsAlongProfileForMicropittingCalculation = int(value) if value else 0

    @property
    def tip_relief_in_scuffing_calculation(self) -> '_447.TipReliefScuffingOptions':
        '''TipReliefScuffingOptions: 'TipReliefInScuffingCalculation' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.TipReliefInScuffingCalculation)
        return constructor.new(_447.TipReliefScuffingOptions)(value) if value is not None else None

    @tip_relief_in_scuffing_calculation.setter
    def tip_relief_in_scuffing_calculation(self, value: '_447.TipReliefScuffingOptions'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.TipReliefInScuffingCalculation = value

    @property
    def dynamic_factor_method(self) -> '_434.DynamicFactorMethods':
        '''DynamicFactorMethods: 'DynamicFactorMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.DynamicFactorMethod)
        return constructor.new(_434.DynamicFactorMethods)(value) if value is not None else None

    @dynamic_factor_method.setter
    def dynamic_factor_method(self, value: '_434.DynamicFactorMethods'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.DynamicFactorMethod = value

    @property
    def include_rim_thickness_factor(self) -> 'bool':
        '''bool: 'IncludeRimThicknessFactor' is the original name of this property.'''

        return self.wrapped.IncludeRimThicknessFactor

    @include_rim_thickness_factor.setter
    def include_rim_thickness_factor(self, value: 'bool'):
        self.wrapped.IncludeRimThicknessFactor = bool(value) if value else False

    @property
    def gear_blank_factor_calculation_option(self) -> '_435.GearBlankFactorCalculationOptions':
        '''GearBlankFactorCalculationOptions: 'GearBlankFactorCalculationOption' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.GearBlankFactorCalculationOption)
        return constructor.new(_435.GearBlankFactorCalculationOptions)(value) if value is not None else None

    @gear_blank_factor_calculation_option.setter
    def gear_blank_factor_calculation_option(self, value: '_435.GearBlankFactorCalculationOptions'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.GearBlankFactorCalculationOption = value

    @property
    def use_10_for_contact_ratio_factor_contact_for_spur_gears_with_contact_ratio_less_than_20(self) -> 'bool':
        '''bool: 'Use10ForContactRatioFactorContactForSpurGearsWithContactRatioLessThan20' is the original name of this property.'''

        return self.wrapped.Use10ForContactRatioFactorContactForSpurGearsWithContactRatioLessThan20

    @use_10_for_contact_ratio_factor_contact_for_spur_gears_with_contact_ratio_less_than_20.setter
    def use_10_for_contact_ratio_factor_contact_for_spur_gears_with_contact_ratio_less_than_20(self, value: 'bool'):
        self.wrapped.Use10ForContactRatioFactorContactForSpurGearsWithContactRatioLessThan20 = bool(value) if value else False

    @property
    def apply_application_and_dynamic_factor_by_default(self) -> 'bool':
        '''bool: 'ApplyApplicationAndDynamicFactorByDefault' is the original name of this property.'''

        return self.wrapped.ApplyApplicationAndDynamicFactorByDefault

    @apply_application_and_dynamic_factor_by_default.setter
    def apply_application_and_dynamic_factor_by_default(self, value: 'bool'):
        self.wrapped.ApplyApplicationAndDynamicFactorByDefault = bool(value) if value else False

    @property
    def allow_transverse_contact_ratio_less_than_one(self) -> 'bool':
        '''bool: 'AllowTransverseContactRatioLessThanOne' is the original name of this property.'''

        return self.wrapped.AllowTransverseContactRatioLessThanOne

    @allow_transverse_contact_ratio_less_than_one.setter
    def allow_transverse_contact_ratio_less_than_one(self, value: 'bool'):
        self.wrapped.AllowTransverseContactRatioLessThanOne = bool(value) if value else False

    @property
    def film_thickness_equation_for_scuffing(self) -> '_444.ScuffingMethods':
        '''ScuffingMethods: 'FilmThicknessEquationForScuffing' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.FilmThicknessEquationForScuffing)
        return constructor.new(_444.ScuffingMethods)(value) if value is not None else None

    @film_thickness_equation_for_scuffing.setter
    def film_thickness_equation_for_scuffing(self, value: '_444.ScuffingMethods'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.FilmThicknessEquationForScuffing = value

    @property
    def micropitting_rating_method(self) -> '_438.MicropittingRatingMethod':
        '''MicropittingRatingMethod: 'MicropittingRatingMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.MicropittingRatingMethod)
        return constructor.new(_438.MicropittingRatingMethod)(value) if value is not None else None

    @micropitting_rating_method.setter
    def micropitting_rating_method(self, value: '_438.MicropittingRatingMethod'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.MicropittingRatingMethod = value

    @property
    def scuffing_rating_method_flash_temperature_method(self) -> 'enum_with_selected_value.EnumWithSelectedValue_ScuffingFlashTemperatureRatingMethod':
        '''enum_with_selected_value.EnumWithSelectedValue_ScuffingFlashTemperatureRatingMethod: 'ScuffingRatingMethodFlashTemperatureMethod' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_ScuffingFlashTemperatureRatingMethod.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.ScuffingRatingMethodFlashTemperatureMethod, value) if self.wrapped.ScuffingRatingMethodFlashTemperatureMethod is not None else None

    @scuffing_rating_method_flash_temperature_method.setter
    def scuffing_rating_method_flash_temperature_method(self, value: 'enum_with_selected_value.EnumWithSelectedValue_ScuffingFlashTemperatureRatingMethod.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_ScuffingFlashTemperatureRatingMethod.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.ScuffingRatingMethodFlashTemperatureMethod = value

    @property
    def scuffing_rating_method_integral_temperature_method(self) -> 'enum_with_selected_value.EnumWithSelectedValue_ScuffingIntegralTemperatureRatingMethod':
        '''enum_with_selected_value.EnumWithSelectedValue_ScuffingIntegralTemperatureRatingMethod: 'ScuffingRatingMethodIntegralTemperatureMethod' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_ScuffingIntegralTemperatureRatingMethod.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.ScuffingRatingMethodIntegralTemperatureMethod, value) if self.wrapped.ScuffingRatingMethodIntegralTemperatureMethod is not None else None

    @scuffing_rating_method_integral_temperature_method.setter
    def scuffing_rating_method_integral_temperature_method(self, value: 'enum_with_selected_value.EnumWithSelectedValue_ScuffingIntegralTemperatureRatingMethod.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_ScuffingIntegralTemperatureRatingMethod.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.ScuffingRatingMethodIntegralTemperatureMethod = value

    @property
    def rating_method(self) -> 'enum_with_selected_value.EnumWithSelectedValue_CylindricalGearRatingMethods':
        '''enum_with_selected_value.EnumWithSelectedValue_CylindricalGearRatingMethods: 'RatingMethod' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_CylindricalGearRatingMethods.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.RatingMethod, value) if self.wrapped.RatingMethod is not None else None

    @rating_method.setter
    def rating_method(self, value: 'enum_with_selected_value.EnumWithSelectedValue_CylindricalGearRatingMethods.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_CylindricalGearRatingMethods.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.RatingMethod = value

    @property
    def agma_stress_cycle_factor_influence_factor(self) -> 'float':
        '''float: 'AGMAStressCycleFactorInfluenceFactor' is the original name of this property.'''

        return self.wrapped.AGMAStressCycleFactorInfluenceFactor

    @agma_stress_cycle_factor_influence_factor.setter
    def agma_stress_cycle_factor_influence_factor(self, value: 'float'):
        self.wrapped.AGMAStressCycleFactorInfluenceFactor = float(value) if value else 0.0

    @property
    def permissible_bending_stress_method(self) -> '_441.RatingMethod':
        '''RatingMethod: 'PermissibleBendingStressMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.PermissibleBendingStressMethod)
        return constructor.new(_441.RatingMethod)(value) if value is not None else None

    @permissible_bending_stress_method.setter
    def permissible_bending_stress_method(self, value: '_441.RatingMethod'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.PermissibleBendingStressMethod = value

    @property
    def use_ltca_stresses_in_gear_rating(self) -> 'bool':
        '''bool: 'UseLTCAStressesInGearRating' is the original name of this property.'''

        return self.wrapped.UseLTCAStressesInGearRating

    @use_ltca_stresses_in_gear_rating.setter
    def use_ltca_stresses_in_gear_rating(self, value: 'bool'):
        self.wrapped.UseLTCAStressesInGearRating = bool(value) if value else False

    @property
    def always_use_chosen_tooth_thickness_for_bending_strength(self) -> 'bool':
        '''bool: 'AlwaysUseChosenToothThicknessForBendingStrength' is the original name of this property.'''

        return self.wrapped.AlwaysUseChosenToothThicknessForBendingStrength

    @always_use_chosen_tooth_thickness_for_bending_strength.setter
    def always_use_chosen_tooth_thickness_for_bending_strength(self, value: 'bool'):
        self.wrapped.AlwaysUseChosenToothThicknessForBendingStrength = bool(value) if value else False

    @property
    def chosen_tooth_thickness_for_bending_strength(self) -> '_448.ToothThicknesses':
        '''ToothThicknesses: 'ChosenToothThicknessForBendingStrength' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ChosenToothThicknessForBendingStrength)
        return constructor.new(_448.ToothThicknesses)(value) if value is not None else None

    @chosen_tooth_thickness_for_bending_strength.setter
    def chosen_tooth_thickness_for_bending_strength(self, value: '_448.ToothThicknesses'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ChosenToothThicknessForBendingStrength = value

    @property
    def show_vdi_rating_when_available(self) -> 'bool':
        '''bool: 'ShowVDIRatingWhenAvailable' is the original name of this property.'''

        return self.wrapped.ShowVDIRatingWhenAvailable

    @show_vdi_rating_when_available.setter
    def show_vdi_rating_when_available(self, value: 'bool'):
        self.wrapped.ShowVDIRatingWhenAvailable = bool(value) if value else False

    @property
    def vdi_rating_geometry_calculation_method(self) -> 'overridable.Overridable_CylindricalGearRatingMethods':
        '''overridable.Overridable_CylindricalGearRatingMethods: 'VDIRatingGeometryCalculationMethod' is the original name of this property.'''

        value = overridable.Overridable_CylindricalGearRatingMethods.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.VDIRatingGeometryCalculationMethod, value) if self.wrapped.VDIRatingGeometryCalculationMethod is not None else None

    @vdi_rating_geometry_calculation_method.setter
    def vdi_rating_geometry_calculation_method(self, value: 'overridable.Overridable_CylindricalGearRatingMethods.implicit_type()'):
        wrapper_type = overridable.Overridable_CylindricalGearRatingMethods.wrapper_type()
        enclosed_type = overridable.Overridable_CylindricalGearRatingMethods.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value if value is not None else None, is_overridden)
        self.wrapped.VDIRatingGeometryCalculationMethod = value

    @property
    def use_point_of_highest_stress_to_calculate_face_load_factor(self) -> 'bool':
        '''bool: 'UsePointOfHighestStressToCalculateFaceLoadFactor' is the original name of this property.'''

        return self.wrapped.UsePointOfHighestStressToCalculateFaceLoadFactor

    @use_point_of_highest_stress_to_calculate_face_load_factor.setter
    def use_point_of_highest_stress_to_calculate_face_load_factor(self, value: 'bool'):
        self.wrapped.UsePointOfHighestStressToCalculateFaceLoadFactor = bool(value) if value else False

    @property
    def use_interpolated_single_pair_tooth_contact_factor_for_hcr_helical_gears(self) -> 'bool':
        '''bool: 'UseInterpolatedSinglePairToothContactFactorForHCRHelicalGears' is the original name of this property.'''

        return self.wrapped.UseInterpolatedSinglePairToothContactFactorForHCRHelicalGears

    @use_interpolated_single_pair_tooth_contact_factor_for_hcr_helical_gears.setter
    def use_interpolated_single_pair_tooth_contact_factor_for_hcr_helical_gears(self, value: 'bool'):
        self.wrapped.UseInterpolatedSinglePairToothContactFactorForHCRHelicalGears = bool(value) if value else False

    @property
    def internal_gear_root_fillet_radius_is_always_equal_to_basic_rack_root_fillet_radius(self) -> 'bool':
        '''bool: 'InternalGearRootFilletRadiusIsAlwaysEqualToBasicRackRootFilletRadius' is the original name of this property.'''

        return self.wrapped.InternalGearRootFilletRadiusIsAlwaysEqualToBasicRackRootFilletRadius

    @internal_gear_root_fillet_radius_is_always_equal_to_basic_rack_root_fillet_radius.setter
    def internal_gear_root_fillet_radius_is_always_equal_to_basic_rack_root_fillet_radius(self, value: 'bool'):
        self.wrapped.InternalGearRootFilletRadiusIsAlwaysEqualToBasicRackRootFilletRadius = bool(value) if value else False

    @property
    def mean_coefficient_of_friction_flash_temperature_method(self) -> 'float':
        '''float: 'MeanCoefficientOfFrictionFlashTemperatureMethod' is the original name of this property.'''

        return self.wrapped.MeanCoefficientOfFrictionFlashTemperatureMethod

    @mean_coefficient_of_friction_flash_temperature_method.setter
    def mean_coefficient_of_friction_flash_temperature_method(self, value: 'float'):
        self.wrapped.MeanCoefficientOfFrictionFlashTemperatureMethod = float(value) if value else 0.0

    @property
    def number_of_points_along_profile_for_tooth_flank_fracture_calculation(self) -> 'int':
        '''int: 'NumberOfPointsAlongProfileForToothFlankFractureCalculation' is the original name of this property.'''

        return self.wrapped.NumberOfPointsAlongProfileForToothFlankFractureCalculation

    @number_of_points_along_profile_for_tooth_flank_fracture_calculation.setter
    def number_of_points_along_profile_for_tooth_flank_fracture_calculation(self, value: 'int'):
        self.wrapped.NumberOfPointsAlongProfileForToothFlankFractureCalculation = int(value) if value else 0

    @property
    def apply_work_hardening_factor_for_wrought_normalised_low_carbon_steel_and_cast_steel(self) -> 'bool':
        '''bool: 'ApplyWorkHardeningFactorForWroughtNormalisedLowCarbonSteelAndCastSteel' is the original name of this property.'''

        return self.wrapped.ApplyWorkHardeningFactorForWroughtNormalisedLowCarbonSteelAndCastSteel

    @apply_work_hardening_factor_for_wrought_normalised_low_carbon_steel_and_cast_steel.setter
    def apply_work_hardening_factor_for_wrought_normalised_low_carbon_steel_and_cast_steel(self, value: 'bool'):
        self.wrapped.ApplyWorkHardeningFactorForWroughtNormalisedLowCarbonSteelAndCastSteel = bool(value) if value else False

    @property
    def limit_dynamic_factor_if_not_in_main_resonance_range_by_default(self) -> 'bool':
        '''bool: 'LimitDynamicFactorIfNotInMainResonanceRangeByDefault' is the original name of this property.'''

        return self.wrapped.LimitDynamicFactorIfNotInMainResonanceRangeByDefault

    @limit_dynamic_factor_if_not_in_main_resonance_range_by_default.setter
    def limit_dynamic_factor_if_not_in_main_resonance_range_by_default(self, value: 'bool'):
        self.wrapped.LimitDynamicFactorIfNotInMainResonanceRangeByDefault = bool(value) if value else False

    @property
    def limit_micro_geometry_factor_for_the_dynamic_load_by_default(self) -> 'bool':
        '''bool: 'LimitMicroGeometryFactorForTheDynamicLoadByDefault' is the original name of this property.'''

        return self.wrapped.LimitMicroGeometryFactorForTheDynamicLoadByDefault

    @limit_micro_geometry_factor_for_the_dynamic_load_by_default.setter
    def limit_micro_geometry_factor_for_the_dynamic_load_by_default(self, value: 'bool'):
        self.wrapped.LimitMicroGeometryFactorForTheDynamicLoadByDefault = bool(value) if value else False
