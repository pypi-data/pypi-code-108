'''_5188.py

MBDRunUpAnalysisOptions
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.system_model.analyses_and_results.mbd_analyses import _5174, _5213, _5208
from mastapy._internal.implicit import list_with_selected_item
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.system_model.analyses_and_results.analysis_cases import _7253
from mastapy.system_model.analyses_and_results.static_loads import _6520
from mastapy._internal.python_net import python_net_import

_MBD_RUN_UP_ANALYSIS_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'MBDRunUpAnalysisOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('MBDRunUpAnalysisOptions',)


class MBDRunUpAnalysisOptions(_7253.AbstractAnalysisOptions['_6520.TimeSeriesLoadCase']):
    '''MBDRunUpAnalysisOptions

    This is a mastapy class.
    '''

    TYPE = _MBD_RUN_UP_ANALYSIS_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MBDRunUpAnalysisOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def time_to_reach_minimum_speed(self) -> 'float':
        '''float: 'TimeToReachMinimumSpeed' is the original name of this property.'''

        return self.wrapped.TimeToReachMinimumSpeed

    @time_to_reach_minimum_speed.setter
    def time_to_reach_minimum_speed(self, value: 'float'):
        self.wrapped.TimeToReachMinimumSpeed = float(value) if value else 0.0

    @property
    def time_to_keep_linear_speed_before_reaching_minimum_speed(self) -> 'float':
        '''float: 'TimeToKeepLinearSpeedBeforeReachingMinimumSpeed' is the original name of this property.'''

        return self.wrapped.TimeToKeepLinearSpeedBeforeReachingMinimumSpeed

    @time_to_keep_linear_speed_before_reaching_minimum_speed.setter
    def time_to_keep_linear_speed_before_reaching_minimum_speed(self, value: 'float'):
        self.wrapped.TimeToKeepLinearSpeedBeforeReachingMinimumSpeed = float(value) if value else 0.0

    @property
    def polynomial_order(self) -> 'int':
        '''int: 'PolynomialOrder' is the original name of this property.'''

        return self.wrapped.PolynomialOrder

    @polynomial_order.setter
    def polynomial_order(self, value: 'int'):
        self.wrapped.PolynomialOrder = int(value) if value else 0

    @property
    def input_velocity_processing_type(self) -> '_5174.InputVelocityForRunUpProcessingType':
        '''InputVelocityForRunUpProcessingType: 'InputVelocityProcessingType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.InputVelocityProcessingType)
        return constructor.new(_5174.InputVelocityForRunUpProcessingType)(value) if value is not None else None

    @input_velocity_processing_type.setter
    def input_velocity_processing_type(self, value: '_5174.InputVelocityForRunUpProcessingType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.InputVelocityProcessingType = value

    @property
    def power_load_for_run_up_torque(self) -> 'list_with_selected_item.ListWithSelectedItem_str':
        '''list_with_selected_item.ListWithSelectedItem_str: 'PowerLoadForRunUpTorque' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_str)(self.wrapped.PowerLoadForRunUpTorque) if self.wrapped.PowerLoadForRunUpTorque is not None else None

    @power_load_for_run_up_torque.setter
    def power_load_for_run_up_torque(self, value: 'list_with_selected_item.ListWithSelectedItem_str.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_str.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_str.implicit_type()
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else '')
        self.wrapped.PowerLoadForRunUpTorque = value

    @property
    def shape_of_initial_acceleration_period(self) -> '_5213.ShapeOfInitialAccelerationPeriodForRunUp':
        '''ShapeOfInitialAccelerationPeriodForRunUp: 'ShapeOfInitialAccelerationPeriod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ShapeOfInitialAccelerationPeriod)
        return constructor.new(_5213.ShapeOfInitialAccelerationPeriodForRunUp)(value) if value is not None else None

    @shape_of_initial_acceleration_period.setter
    def shape_of_initial_acceleration_period(self, value: '_5213.ShapeOfInitialAccelerationPeriodForRunUp'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ShapeOfInitialAccelerationPeriod = value

    @property
    def run_up_driving_mode(self) -> '_5208.RunUpDrivingMode':
        '''RunUpDrivingMode: 'RunUpDrivingMode' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.RunUpDrivingMode)
        return constructor.new(_5208.RunUpDrivingMode)(value) if value is not None else None

    @run_up_driving_mode.setter
    def run_up_driving_mode(self, value: '_5208.RunUpDrivingMode'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.RunUpDrivingMode = value

    @property
    def run_up_start_speed(self) -> 'float':
        '''float: 'RunUpStartSpeed' is the original name of this property.'''

        return self.wrapped.RunUpStartSpeed

    @run_up_start_speed.setter
    def run_up_start_speed(self, value: 'float'):
        self.wrapped.RunUpStartSpeed = float(value) if value else 0.0

    @property
    def run_up_end_speed(self) -> 'float':
        '''float: 'RunUpEndSpeed' is the original name of this property.'''

        return self.wrapped.RunUpEndSpeed

    @run_up_end_speed.setter
    def run_up_end_speed(self, value: 'float'):
        self.wrapped.RunUpEndSpeed = float(value) if value else 0.0

    @property
    def reference_power_load_for_run_up_speed(self) -> 'list_with_selected_item.ListWithSelectedItem_str':
        '''list_with_selected_item.ListWithSelectedItem_str: 'ReferencePowerLoadForRunUpSpeed' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_str)(self.wrapped.ReferencePowerLoadForRunUpSpeed) if self.wrapped.ReferencePowerLoadForRunUpSpeed is not None else None

    @reference_power_load_for_run_up_speed.setter
    def reference_power_load_for_run_up_speed(self, value: 'list_with_selected_item.ListWithSelectedItem_str.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_str.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_str.implicit_type()
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else '')
        self.wrapped.ReferencePowerLoadForRunUpSpeed = value

    @property
    def run_down_after(self) -> 'bool':
        '''bool: 'RunDownAfter' is the original name of this property.'''

        return self.wrapped.RunDownAfter

    @run_down_after.setter
    def run_down_after(self, value: 'bool'):
        self.wrapped.RunDownAfter = bool(value) if value else False

    @property
    def time_to_change_direction(self) -> 'float':
        '''float: 'TimeToChangeDirection' is the original name of this property.'''

        return self.wrapped.TimeToChangeDirection

    @time_to_change_direction.setter
    def time_to_change_direction(self, value: 'float'):
        self.wrapped.TimeToChangeDirection = float(value) if value else 0.0
