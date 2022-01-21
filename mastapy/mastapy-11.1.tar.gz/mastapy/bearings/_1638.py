'''_1638.py

BearingSettings
'''


from mastapy._internal.implicit import enum_with_selected_value
from mastapy.bearings import (
    _1648, _1647, _1640, _1641
)
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import enum_with_selected_value_runtime, conversion, constructor
from mastapy.bearings.bearing_results.rolling.skf_module import _1845
from mastapy.utility import _1387
from mastapy._internal.python_net import python_net_import

_BEARING_SETTINGS = python_net_import('SMT.MastaAPI.Bearings', 'BearingSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingSettings',)


class BearingSettings(_1387.PerMachineSettings):
    '''BearingSettings

    This is a mastapy class.
    '''

    TYPE = _BEARING_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BearingSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def default_roller_profile(self) -> 'enum_with_selected_value.EnumWithSelectedValue_RollerBearingProfileTypes':
        '''enum_with_selected_value.EnumWithSelectedValue_RollerBearingProfileTypes: 'DefaultRollerProfile' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_RollerBearingProfileTypes.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.DefaultRollerProfile, value) if self.wrapped.DefaultRollerProfile is not None else None

    @default_roller_profile.setter
    def default_roller_profile(self, value: 'enum_with_selected_value.EnumWithSelectedValue_RollerBearingProfileTypes.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_RollerBearingProfileTypes.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.DefaultRollerProfile = value

    @property
    def tolerance_used_for_diameter_warnings_and_database_filter(self) -> 'float':
        '''float: 'ToleranceUsedForDiameterWarningsAndDatabaseFilter' is the original name of this property.'''

        return self.wrapped.ToleranceUsedForDiameterWarningsAndDatabaseFilter

    @tolerance_used_for_diameter_warnings_and_database_filter.setter
    def tolerance_used_for_diameter_warnings_and_database_filter(self, value: 'float'):
        self.wrapped.ToleranceUsedForDiameterWarningsAndDatabaseFilter = float(value) if value else 0.0

    @property
    def failure_probability_for_rating_life_percent(self) -> '_1647.RatingLife':
        '''RatingLife: 'FailureProbabilityForRatingLifePercent' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.FailureProbabilityForRatingLifePercent)
        return constructor.new(_1647.RatingLife)(value) if value is not None else None

    @failure_probability_for_rating_life_percent.setter
    def failure_probability_for_rating_life_percent(self, value: '_1647.RatingLife'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.FailureProbabilityForRatingLifePercent = value

    @property
    def use_plain_journal_bearing_misalignment_factors(self) -> 'bool':
        '''bool: 'UsePlainJournalBearingMisalignmentFactors' is the original name of this property.'''

        return self.wrapped.UsePlainJournalBearingMisalignmentFactors

    @use_plain_journal_bearing_misalignment_factors.setter
    def use_plain_journal_bearing_misalignment_factors(self, value: 'bool'):
        self.wrapped.UsePlainJournalBearingMisalignmentFactors = bool(value) if value else False

    @property
    def include_exponent_and_reduction_factors_in_isots162812008(self) -> '_1640.ExponentAndReductionFactorsInISO16281Calculation':
        '''ExponentAndReductionFactorsInISO16281Calculation: 'IncludeExponentAndReductionFactorsInISOTS162812008' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.IncludeExponentAndReductionFactorsInISOTS162812008)
        return constructor.new(_1640.ExponentAndReductionFactorsInISO16281Calculation)(value) if value is not None else None

    @include_exponent_and_reduction_factors_in_isots162812008.setter
    def include_exponent_and_reduction_factors_in_isots162812008(self, value: '_1640.ExponentAndReductionFactorsInISO16281Calculation'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.IncludeExponentAndReductionFactorsInISOTS162812008 = value

    @property
    def lubricant_film_temperature_calculation_pressure_fed_grease_filled_bearings(self) -> 'enum_with_selected_value.EnumWithSelectedValue_FluidFilmTemperatureOptions':
        '''enum_with_selected_value.EnumWithSelectedValue_FluidFilmTemperatureOptions: 'LubricantFilmTemperatureCalculationPressureFedGreaseFilledBearings' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_FluidFilmTemperatureOptions.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.LubricantFilmTemperatureCalculationPressureFedGreaseFilledBearings, value) if self.wrapped.LubricantFilmTemperatureCalculationPressureFedGreaseFilledBearings is not None else None

    @lubricant_film_temperature_calculation_pressure_fed_grease_filled_bearings.setter
    def lubricant_film_temperature_calculation_pressure_fed_grease_filled_bearings(self, value: 'enum_with_selected_value.EnumWithSelectedValue_FluidFilmTemperatureOptions.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_FluidFilmTemperatureOptions.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.LubricantFilmTemperatureCalculationPressureFedGreaseFilledBearings = value

    @property
    def lubricant_film_temperature_calculation_splashed_submerged_bearings(self) -> 'enum_with_selected_value.EnumWithSelectedValue_FluidFilmTemperatureOptions':
        '''enum_with_selected_value.EnumWithSelectedValue_FluidFilmTemperatureOptions: 'LubricantFilmTemperatureCalculationSplashedSubmergedBearings' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_FluidFilmTemperatureOptions.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.LubricantFilmTemperatureCalculationSplashedSubmergedBearings, value) if self.wrapped.LubricantFilmTemperatureCalculationSplashedSubmergedBearings is not None else None

    @lubricant_film_temperature_calculation_splashed_submerged_bearings.setter
    def lubricant_film_temperature_calculation_splashed_submerged_bearings(self, value: 'enum_with_selected_value.EnumWithSelectedValue_FluidFilmTemperatureOptions.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_FluidFilmTemperatureOptions.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.LubricantFilmTemperatureCalculationSplashedSubmergedBearings = value

    @property
    def ball_bearing_weibull_reliability_slope(self) -> 'float':
        '''float: 'BallBearingWeibullReliabilitySlope' is the original name of this property.'''

        return self.wrapped.BallBearingWeibullReliabilitySlope

    @ball_bearing_weibull_reliability_slope.setter
    def ball_bearing_weibull_reliability_slope(self, value: 'float'):
        self.wrapped.BallBearingWeibullReliabilitySlope = float(value) if value else 0.0

    @property
    def roller_bearing_weibull_reliability_slope(self) -> 'float':
        '''float: 'RollerBearingWeibullReliabilitySlope' is the original name of this property.'''

        return self.wrapped.RollerBearingWeibullReliabilitySlope

    @roller_bearing_weibull_reliability_slope.setter
    def roller_bearing_weibull_reliability_slope(self, value: 'float'):
        self.wrapped.RollerBearingWeibullReliabilitySlope = float(value) if value else 0.0

    @property
    def third_weibull_parameter(self) -> 'float':
        '''float: 'ThirdWeibullParameter' is the original name of this property.'''

        return self.wrapped.ThirdWeibullParameter

    @third_weibull_parameter.setter
    def third_weibull_parameter(self, value: 'float'):
        self.wrapped.ThirdWeibullParameter = float(value) if value else 0.0

    @property
    def enable_skf_module(self) -> 'bool':
        '''bool: 'EnableSKFModule' is the original name of this property.'''

        return self.wrapped.EnableSKFModule

    @enable_skf_module.setter
    def enable_skf_module(self, value: 'bool'):
        self.wrapped.EnableSKFModule = bool(value) if value else False

    @property
    def log_http_requests(self) -> 'bool':
        '''bool: 'LogHTTPRequests' is the original name of this property.'''

        return self.wrapped.LogHTTPRequests

    @log_http_requests.setter
    def log_http_requests(self, value: 'bool'):
        self.wrapped.LogHTTPRequests = bool(value) if value else False

    @property
    def log_file_path(self) -> 'str':
        '''str: 'LogFilePath' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LogFilePath

    @property
    def skf_authentication(self) -> '_1845.SKFAuthentication':
        '''SKFAuthentication: 'SKFAuthentication' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1845.SKFAuthentication)(self.wrapped.SKFAuthentication) if self.wrapped.SKFAuthentication is not None else None
