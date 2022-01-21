'''_542.py

ProfileModification
'''


from mastapy._internal.implicit import enum_with_selected_value
from mastapy.gears.micro_geometry import (
    _536, _538, _541, _535,
    _537, _540, _534, _533,
    _539
)
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import enum_with_selected_value_runtime, conversion, constructor
from mastapy.math_utility import _1333
from mastapy._internal.python_net import python_net_import

_PROFILE_MODIFICATION = python_net_import('SMT.MastaAPI.Gears.MicroGeometry', 'ProfileModification')


__docformat__ = 'restructuredtext en'
__all__ = ('ProfileModification',)


class ProfileModification(_539.Modification):
    '''ProfileModification

    This is a mastapy class.
    '''

    TYPE = _PROFILE_MODIFICATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ProfileModification.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def location_of_tip_relief_start(self) -> 'enum_with_selected_value.EnumWithSelectedValue_LocationOfTipReliefEvaluation':
        '''enum_with_selected_value.EnumWithSelectedValue_LocationOfTipReliefEvaluation: 'LocationOfTipReliefStart' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_LocationOfTipReliefEvaluation.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.LocationOfTipReliefStart, value) if self.wrapped.LocationOfTipReliefStart is not None else None

    @location_of_tip_relief_start.setter
    def location_of_tip_relief_start(self, value: 'enum_with_selected_value.EnumWithSelectedValue_LocationOfTipReliefEvaluation.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_LocationOfTipReliefEvaluation.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.LocationOfTipReliefStart = value

    @property
    def main_profile_modification_ends_at_the_start_of_tip_relief(self) -> '_538.MainProfileReliefEndsAtTheStartOfTipReliefOption':
        '''MainProfileReliefEndsAtTheStartOfTipReliefOption: 'MainProfileModificationEndsAtTheStartOfTipRelief' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.MainProfileModificationEndsAtTheStartOfTipRelief)
        return constructor.new(_538.MainProfileReliefEndsAtTheStartOfTipReliefOption)(value) if value is not None else None

    @main_profile_modification_ends_at_the_start_of_tip_relief.setter
    def main_profile_modification_ends_at_the_start_of_tip_relief(self, value: '_538.MainProfileReliefEndsAtTheStartOfTipReliefOption'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.MainProfileModificationEndsAtTheStartOfTipRelief = value

    @property
    def measure_tip_reliefs_from_extrapolated_linear_relief(self) -> 'bool':
        '''bool: 'MeasureTipReliefsFromExtrapolatedLinearRelief' is the original name of this property.'''

        return self.wrapped.MeasureTipReliefsFromExtrapolatedLinearRelief

    @measure_tip_reliefs_from_extrapolated_linear_relief.setter
    def measure_tip_reliefs_from_extrapolated_linear_relief(self, value: 'bool'):
        self.wrapped.MeasureTipReliefsFromExtrapolatedLinearRelief = bool(value) if value else False

    @property
    def location_of_tip_relief_evaluation(self) -> 'enum_with_selected_value.EnumWithSelectedValue_LocationOfTipReliefEvaluation':
        '''enum_with_selected_value.EnumWithSelectedValue_LocationOfTipReliefEvaluation: 'LocationOfTipReliefEvaluation' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_LocationOfTipReliefEvaluation.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.LocationOfTipReliefEvaluation, value) if self.wrapped.LocationOfTipReliefEvaluation is not None else None

    @location_of_tip_relief_evaluation.setter
    def location_of_tip_relief_evaluation(self, value: 'enum_with_selected_value.EnumWithSelectedValue_LocationOfTipReliefEvaluation.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_LocationOfTipReliefEvaluation.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.LocationOfTipReliefEvaluation = value

    @property
    def evaluation_of_linear_tip_relief_factor(self) -> 'float':
        '''float: 'EvaluationOfLinearTipReliefFactor' is the original name of this property.'''

        return self.wrapped.EvaluationOfLinearTipReliefFactor

    @evaluation_of_linear_tip_relief_factor.setter
    def evaluation_of_linear_tip_relief_factor(self, value: 'float'):
        self.wrapped.EvaluationOfLinearTipReliefFactor = float(value) if value else 0.0

    @property
    def evaluation_of_parabolic_tip_relief_factor(self) -> 'float':
        '''float: 'EvaluationOfParabolicTipReliefFactor' is the original name of this property.'''

        return self.wrapped.EvaluationOfParabolicTipReliefFactor

    @evaluation_of_parabolic_tip_relief_factor.setter
    def evaluation_of_parabolic_tip_relief_factor(self, value: 'float'):
        self.wrapped.EvaluationOfParabolicTipReliefFactor = float(value) if value else 0.0

    @property
    def parabolic_tip_relief_starts_tangent_to_main_profile_relief(self) -> '_541.ParabolicTipReliefStartsTangentToMainProfileRelief':
        '''ParabolicTipReliefStartsTangentToMainProfileRelief: 'ParabolicTipReliefStartsTangentToMainProfileRelief' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ParabolicTipReliefStartsTangentToMainProfileRelief)
        return constructor.new(_541.ParabolicTipReliefStartsTangentToMainProfileRelief)(value) if value is not None else None

    @parabolic_tip_relief_starts_tangent_to_main_profile_relief.setter
    def parabolic_tip_relief_starts_tangent_to_main_profile_relief(self, value: '_541.ParabolicTipReliefStartsTangentToMainProfileRelief'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ParabolicTipReliefStartsTangentToMainProfileRelief = value

    @property
    def location_of_root_modification_start(self) -> 'enum_with_selected_value.EnumWithSelectedValue_LocationOfRootReliefEvaluation':
        '''enum_with_selected_value.EnumWithSelectedValue_LocationOfRootReliefEvaluation: 'LocationOfRootModificationStart' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_LocationOfRootReliefEvaluation.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.LocationOfRootModificationStart, value) if self.wrapped.LocationOfRootModificationStart is not None else None

    @location_of_root_modification_start.setter
    def location_of_root_modification_start(self, value: 'enum_with_selected_value.EnumWithSelectedValue_LocationOfRootReliefEvaluation.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_LocationOfRootReliefEvaluation.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.LocationOfRootModificationStart = value

    @property
    def main_profile_modification_ends_at_the_start_of_root_relief(self) -> '_537.MainProfileReliefEndsAtTheStartOfRootReliefOption':
        '''MainProfileReliefEndsAtTheStartOfRootReliefOption: 'MainProfileModificationEndsAtTheStartOfRootRelief' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.MainProfileModificationEndsAtTheStartOfRootRelief)
        return constructor.new(_537.MainProfileReliefEndsAtTheStartOfRootReliefOption)(value) if value is not None else None

    @main_profile_modification_ends_at_the_start_of_root_relief.setter
    def main_profile_modification_ends_at_the_start_of_root_relief(self, value: '_537.MainProfileReliefEndsAtTheStartOfRootReliefOption'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.MainProfileModificationEndsAtTheStartOfRootRelief = value

    @property
    def measure_root_reliefs_from_extrapolated_linear_relief(self) -> 'bool':
        '''bool: 'MeasureRootReliefsFromExtrapolatedLinearRelief' is the original name of this property.'''

        return self.wrapped.MeasureRootReliefsFromExtrapolatedLinearRelief

    @measure_root_reliefs_from_extrapolated_linear_relief.setter
    def measure_root_reliefs_from_extrapolated_linear_relief(self, value: 'bool'):
        self.wrapped.MeasureRootReliefsFromExtrapolatedLinearRelief = bool(value) if value else False

    @property
    def location_of_root_relief_evaluation(self) -> 'enum_with_selected_value.EnumWithSelectedValue_LocationOfRootReliefEvaluation':
        '''enum_with_selected_value.EnumWithSelectedValue_LocationOfRootReliefEvaluation: 'LocationOfRootReliefEvaluation' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_LocationOfRootReliefEvaluation.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.LocationOfRootReliefEvaluation, value) if self.wrapped.LocationOfRootReliefEvaluation is not None else None

    @location_of_root_relief_evaluation.setter
    def location_of_root_relief_evaluation(self, value: 'enum_with_selected_value.EnumWithSelectedValue_LocationOfRootReliefEvaluation.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_LocationOfRootReliefEvaluation.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.LocationOfRootReliefEvaluation = value

    @property
    def evaluation_of_linear_root_relief_factor(self) -> 'float':
        '''float: 'EvaluationOfLinearRootReliefFactor' is the original name of this property.'''

        return self.wrapped.EvaluationOfLinearRootReliefFactor

    @evaluation_of_linear_root_relief_factor.setter
    def evaluation_of_linear_root_relief_factor(self, value: 'float'):
        self.wrapped.EvaluationOfLinearRootReliefFactor = float(value) if value else 0.0

    @property
    def evaluation_of_parabolic_root_relief_factor(self) -> 'float':
        '''float: 'EvaluationOfParabolicRootReliefFactor' is the original name of this property.'''

        return self.wrapped.EvaluationOfParabolicRootReliefFactor

    @evaluation_of_parabolic_root_relief_factor.setter
    def evaluation_of_parabolic_root_relief_factor(self, value: 'float'):
        self.wrapped.EvaluationOfParabolicRootReliefFactor = float(value) if value else 0.0

    @property
    def parabolic_root_relief_starts_tangent_to_main_profile_relief(self) -> '_540.ParabolicRootReliefStartsTangentToMainProfileRelief':
        '''ParabolicRootReliefStartsTangentToMainProfileRelief: 'ParabolicRootReliefStartsTangentToMainProfileRelief' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ParabolicRootReliefStartsTangentToMainProfileRelief)
        return constructor.new(_540.ParabolicRootReliefStartsTangentToMainProfileRelief)(value) if value is not None else None

    @parabolic_root_relief_starts_tangent_to_main_profile_relief.setter
    def parabolic_root_relief_starts_tangent_to_main_profile_relief(self, value: '_540.ParabolicRootReliefStartsTangentToMainProfileRelief'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ParabolicRootReliefStartsTangentToMainProfileRelief = value

    @property
    def linear_relief(self) -> 'float':
        '''float: 'LinearRelief' is the original name of this property.'''

        return self.wrapped.LinearRelief

    @linear_relief.setter
    def linear_relief(self, value: 'float'):
        self.wrapped.LinearRelief = float(value) if value else 0.0

    @property
    def barrelling_relief(self) -> 'float':
        '''float: 'BarrellingRelief' is the original name of this property.'''

        return self.wrapped.BarrellingRelief

    @barrelling_relief.setter
    def barrelling_relief(self, value: 'float'):
        self.wrapped.BarrellingRelief = float(value) if value else 0.0

    @property
    def linear_root_relief(self) -> 'float':
        '''float: 'LinearRootRelief' is the original name of this property.'''

        return self.wrapped.LinearRootRelief

    @linear_root_relief.setter
    def linear_root_relief(self, value: 'float'):
        self.wrapped.LinearRootRelief = float(value) if value else 0.0

    @property
    def parabolic_root_relief(self) -> 'float':
        '''float: 'ParabolicRootRelief' is the original name of this property.'''

        return self.wrapped.ParabolicRootRelief

    @parabolic_root_relief.setter
    def parabolic_root_relief(self, value: 'float'):
        self.wrapped.ParabolicRootRelief = float(value) if value else 0.0

    @property
    def linear_tip_relief(self) -> 'float':
        '''float: 'LinearTipRelief' is the original name of this property.'''

        return self.wrapped.LinearTipRelief

    @linear_tip_relief.setter
    def linear_tip_relief(self, value: 'float'):
        self.wrapped.LinearTipRelief = float(value) if value else 0.0

    @property
    def parabolic_tip_relief(self) -> 'float':
        '''float: 'ParabolicTipRelief' is the original name of this property.'''

        return self.wrapped.ParabolicTipRelief

    @parabolic_tip_relief.setter
    def parabolic_tip_relief(self, value: 'float'):
        self.wrapped.ParabolicTipRelief = float(value) if value else 0.0

    @property
    def location_of_evaluation_upper_limit_for_zero_tip_relief(self) -> 'enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationUpperLimit':
        '''enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationUpperLimit: 'LocationOfEvaluationUpperLimitForZeroTipRelief' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationUpperLimit.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.LocationOfEvaluationUpperLimitForZeroTipRelief, value) if self.wrapped.LocationOfEvaluationUpperLimitForZeroTipRelief is not None else None

    @location_of_evaluation_upper_limit_for_zero_tip_relief.setter
    def location_of_evaluation_upper_limit_for_zero_tip_relief(self, value: 'enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationUpperLimit.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationUpperLimit.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.LocationOfEvaluationUpperLimitForZeroTipRelief = value

    @property
    def evaluation_upper_limit_factor_for_zero_tip_relief(self) -> 'float':
        '''float: 'EvaluationUpperLimitFactorForZeroTipRelief' is the original name of this property.'''

        return self.wrapped.EvaluationUpperLimitFactorForZeroTipRelief

    @evaluation_upper_limit_factor_for_zero_tip_relief.setter
    def evaluation_upper_limit_factor_for_zero_tip_relief(self, value: 'float'):
        self.wrapped.EvaluationUpperLimitFactorForZeroTipRelief = float(value) if value else 0.0

    @property
    def location_of_evaluation_upper_limit(self) -> 'enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationUpperLimit':
        '''enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationUpperLimit: 'LocationOfEvaluationUpperLimit' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationUpperLimit.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.LocationOfEvaluationUpperLimit, value) if self.wrapped.LocationOfEvaluationUpperLimit is not None else None

    @location_of_evaluation_upper_limit.setter
    def location_of_evaluation_upper_limit(self, value: 'enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationUpperLimit.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationUpperLimit.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.LocationOfEvaluationUpperLimit = value

    @property
    def evaluation_upper_limit_factor(self) -> 'float':
        '''float: 'EvaluationUpperLimitFactor' is the original name of this property.'''

        return self.wrapped.EvaluationUpperLimitFactor

    @evaluation_upper_limit_factor.setter
    def evaluation_upper_limit_factor(self, value: 'float'):
        self.wrapped.EvaluationUpperLimitFactor = float(value) if value else 0.0

    @property
    def location_of_evaluation_lower_limit_for_zero_root_relief(self) -> 'enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationLowerLimit':
        '''enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationLowerLimit: 'LocationOfEvaluationLowerLimitForZeroRootRelief' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationLowerLimit.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.LocationOfEvaluationLowerLimitForZeroRootRelief, value) if self.wrapped.LocationOfEvaluationLowerLimitForZeroRootRelief is not None else None

    @location_of_evaluation_lower_limit_for_zero_root_relief.setter
    def location_of_evaluation_lower_limit_for_zero_root_relief(self, value: 'enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationLowerLimit.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationLowerLimit.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.LocationOfEvaluationLowerLimitForZeroRootRelief = value

    @property
    def evaluation_lower_limit_factor_for_zero_root_relief(self) -> 'float':
        '''float: 'EvaluationLowerLimitFactorForZeroRootRelief' is the original name of this property.'''

        return self.wrapped.EvaluationLowerLimitFactorForZeroRootRelief

    @evaluation_lower_limit_factor_for_zero_root_relief.setter
    def evaluation_lower_limit_factor_for_zero_root_relief(self, value: 'float'):
        self.wrapped.EvaluationLowerLimitFactorForZeroRootRelief = float(value) if value else 0.0

    @property
    def location_of_evaluation_lower_limit(self) -> 'enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationLowerLimit':
        '''enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationLowerLimit: 'LocationOfEvaluationLowerLimit' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationLowerLimit.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.LocationOfEvaluationLowerLimit, value) if self.wrapped.LocationOfEvaluationLowerLimit is not None else None

    @location_of_evaluation_lower_limit.setter
    def location_of_evaluation_lower_limit(self, value: 'enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationLowerLimit.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationLowerLimit.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.LocationOfEvaluationLowerLimit = value

    @property
    def evaluation_lower_limit_factor(self) -> 'float':
        '''float: 'EvaluationLowerLimitFactor' is the original name of this property.'''

        return self.wrapped.EvaluationLowerLimitFactor

    @evaluation_lower_limit_factor.setter
    def evaluation_lower_limit_factor(self, value: 'float'):
        self.wrapped.EvaluationLowerLimitFactor = float(value) if value else 0.0

    @property
    def start_of_linear_tip_relief_factor(self) -> 'float':
        '''float: 'StartOfLinearTipReliefFactor' is the original name of this property.'''

        return self.wrapped.StartOfLinearTipReliefFactor

    @start_of_linear_tip_relief_factor.setter
    def start_of_linear_tip_relief_factor(self, value: 'float'):
        self.wrapped.StartOfLinearTipReliefFactor = float(value) if value else 0.0

    @property
    def start_of_parabolic_tip_relief_factor(self) -> 'float':
        '''float: 'StartOfParabolicTipReliefFactor' is the original name of this property.'''

        return self.wrapped.StartOfParabolicTipReliefFactor

    @start_of_parabolic_tip_relief_factor.setter
    def start_of_parabolic_tip_relief_factor(self, value: 'float'):
        self.wrapped.StartOfParabolicTipReliefFactor = float(value) if value else 0.0

    @property
    def start_of_linear_root_relief_factor(self) -> 'float':
        '''float: 'StartOfLinearRootReliefFactor' is the original name of this property.'''

        return self.wrapped.StartOfLinearRootReliefFactor

    @start_of_linear_root_relief_factor.setter
    def start_of_linear_root_relief_factor(self, value: 'float'):
        self.wrapped.StartOfLinearRootReliefFactor = float(value) if value else 0.0

    @property
    def start_of_parabolic_root_relief_factor(self) -> 'float':
        '''float: 'StartOfParabolicRootReliefFactor' is the original name of this property.'''

        return self.wrapped.StartOfParabolicRootReliefFactor

    @start_of_parabolic_root_relief_factor.setter
    def start_of_parabolic_root_relief_factor(self, value: 'float'):
        self.wrapped.StartOfParabolicRootReliefFactor = float(value) if value else 0.0

    @property
    def use_user_specified_barrelling_peak_point(self) -> 'bool':
        '''bool: 'UseUserSpecifiedBarrellingPeakPoint' is the original name of this property.'''

        return self.wrapped.UseUserSpecifiedBarrellingPeakPoint

    @use_user_specified_barrelling_peak_point.setter
    def use_user_specified_barrelling_peak_point(self, value: 'bool'):
        self.wrapped.UseUserSpecifiedBarrellingPeakPoint = bool(value) if value else False

    @property
    def barrelling_peak_point_factor(self) -> 'float':
        '''float: 'BarrellingPeakPointFactor' is the original name of this property.'''

        return self.wrapped.BarrellingPeakPointFactor

    @barrelling_peak_point_factor.setter
    def barrelling_peak_point_factor(self, value: 'float'):
        self.wrapped.BarrellingPeakPointFactor = float(value) if value else 0.0

    @property
    def use_measured_data(self) -> 'bool':
        '''bool: 'UseMeasuredData' is the original name of this property.'''

        return self.wrapped.UseMeasuredData

    @use_measured_data.setter
    def use_measured_data(self, value: 'bool'):
        self.wrapped.UseMeasuredData = bool(value) if value else False

    @property
    def measured_data(self) -> '_1333.Vector2DListAccessor':
        '''Vector2DListAccessor: 'MeasuredData' is the original name of this property.'''

        return constructor.new(_1333.Vector2DListAccessor)(self.wrapped.MeasuredData) if self.wrapped.MeasuredData is not None else None

    @measured_data.setter
    def measured_data(self, value: '_1333.Vector2DListAccessor'):
        value = value.wrapped if value else None
        self.wrapped.MeasuredData = value
