'''_83.py

TransientSolverOptions
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy._internal.implicit import enum_with_selected_value
from mastapy.nodal_analysis import (
    _67, _85, _53, _78
)
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_TRANSIENT_SOLVER_OPTIONS = python_net_import('SMT.MastaAPI.NodalAnalysis', 'TransientSolverOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('TransientSolverOptions',)


class TransientSolverOptions(_0.APIBase):
    '''TransientSolverOptions

    This is a mastapy class.
    '''

    TYPE = _TRANSIENT_SOLVER_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TransientSolverOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def maximum_number_of_time_steps(self) -> 'int':
        '''int: 'MaximumNumberOfTimeSteps' is the original name of this property.'''

        return self.wrapped.MaximumNumberOfTimeSteps

    @maximum_number_of_time_steps.setter
    def maximum_number_of_time_steps(self, value: 'int'):
        self.wrapped.MaximumNumberOfTimeSteps = int(value) if value else 0

    @property
    def end_time(self) -> 'float':
        '''float: 'EndTime' is the original name of this property.'''

        return self.wrapped.EndTime

    @end_time.setter
    def end_time(self, value: 'float'):
        self.wrapped.EndTime = float(value) if value else 0.0

    @property
    def maximum_time_step(self) -> 'float':
        '''float: 'MaximumTimeStep' is the original name of this property.'''

        return self.wrapped.MaximumTimeStep

    @maximum_time_step.setter
    def maximum_time_step(self, value: 'float'):
        self.wrapped.MaximumTimeStep = float(value) if value else 0.0

    @property
    def minimum_time_step(self) -> 'float':
        '''float: 'MinimumTimeStep' is the original name of this property.'''

        return self.wrapped.MinimumTimeStep

    @minimum_time_step.setter
    def minimum_time_step(self, value: 'float'):
        self.wrapped.MinimumTimeStep = float(value) if value else 0.0

    @property
    def time_step_length(self) -> 'float':
        '''float: 'TimeStepLength' is the original name of this property.'''

        return self.wrapped.TimeStepLength

    @time_step_length.setter
    def time_step_length(self, value: 'float'):
        self.wrapped.TimeStepLength = float(value) if value else 0.0

    @property
    def integration_method(self) -> 'enum_with_selected_value.EnumWithSelectedValue_IntegrationMethod':
        '''enum_with_selected_value.EnumWithSelectedValue_IntegrationMethod: 'IntegrationMethod' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_IntegrationMethod.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.IntegrationMethod, value) if self.wrapped.IntegrationMethod is not None else None

    @integration_method.setter
    def integration_method(self, value: 'enum_with_selected_value.EnumWithSelectedValue_IntegrationMethod.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_IntegrationMethod.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.IntegrationMethod = value

    @property
    def use_non_linear_solver_for_step(self) -> 'bool':
        '''bool: 'UseNonLinearSolverForStep' is the original name of this property.'''

        return self.wrapped.UseNonLinearSolverForStep

    @use_non_linear_solver_for_step.setter
    def use_non_linear_solver_for_step(self, value: 'bool'):
        self.wrapped.UseNonLinearSolverForStep = bool(value) if value else False

    @property
    def rotate_connections_with_bodies(self) -> 'bool':
        '''bool: 'RotateConnectionsWithBodies' is the original name of this property.'''

        return self.wrapped.RotateConnectionsWithBodies

    @rotate_connections_with_bodies.setter
    def rotate_connections_with_bodies(self, value: 'bool'):
        self.wrapped.RotateConnectionsWithBodies = bool(value) if value else False

    @property
    def theta(self) -> 'float':
        '''float: 'Theta' is the original name of this property.'''

        return self.wrapped.Theta

    @theta.setter
    def theta(self, value: 'float'):
        self.wrapped.Theta = float(value) if value else 0.0

    @property
    def solver_tolerance_input_method(self) -> '_85.TransientSolverToleranceInputMethod':
        '''TransientSolverToleranceInputMethod: 'SolverToleranceInputMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.SolverToleranceInputMethod)
        return constructor.new(_85.TransientSolverToleranceInputMethod)(value) if value is not None else None

    @solver_tolerance_input_method.setter
    def solver_tolerance_input_method(self, value: '_85.TransientSolverToleranceInputMethod'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.SolverToleranceInputMethod = value

    @property
    def absolute_tolerance_angular_velocity_for_step(self) -> 'float':
        '''float: 'AbsoluteToleranceAngularVelocityForStep' is the original name of this property.'''

        return self.wrapped.AbsoluteToleranceAngularVelocityForStep

    @absolute_tolerance_angular_velocity_for_step.setter
    def absolute_tolerance_angular_velocity_for_step(self, value: 'float'):
        self.wrapped.AbsoluteToleranceAngularVelocityForStep = float(value) if value else 0.0

    @property
    def absolute_tolerance_translational_velocity_for_step(self) -> 'float':
        '''float: 'AbsoluteToleranceTranslationalVelocityForStep' is the original name of this property.'''

        return self.wrapped.AbsoluteToleranceTranslationalVelocityForStep

    @absolute_tolerance_translational_velocity_for_step.setter
    def absolute_tolerance_translational_velocity_for_step(self, value: 'float'):
        self.wrapped.AbsoluteToleranceTranslationalVelocityForStep = float(value) if value else 0.0

    @property
    def absolute_tolerance_temperature_for_step(self) -> 'float':
        '''float: 'AbsoluteToleranceTemperatureForStep' is the original name of this property.'''

        return self.wrapped.AbsoluteToleranceTemperatureForStep

    @absolute_tolerance_temperature_for_step.setter
    def absolute_tolerance_temperature_for_step(self, value: 'float'):
        self.wrapped.AbsoluteToleranceTemperatureForStep = float(value) if value else 0.0

    @property
    def relative_tolerance_for_step(self) -> 'float':
        '''float: 'RelativeToleranceForStep' is the original name of this property.'''

        return self.wrapped.RelativeToleranceForStep

    @relative_tolerance_for_step.setter
    def relative_tolerance_for_step(self, value: 'float'):
        self.wrapped.RelativeToleranceForStep = float(value) if value else 0.0

    @property
    def absolute_tolerance_angular_velocity_for_newton_raphson(self) -> 'float':
        '''float: 'AbsoluteToleranceAngularVelocityForNewtonRaphson' is the original name of this property.'''

        return self.wrapped.AbsoluteToleranceAngularVelocityForNewtonRaphson

    @absolute_tolerance_angular_velocity_for_newton_raphson.setter
    def absolute_tolerance_angular_velocity_for_newton_raphson(self, value: 'float'):
        self.wrapped.AbsoluteToleranceAngularVelocityForNewtonRaphson = float(value) if value else 0.0

    @property
    def absolute_tolerance_translational_velocity_for_newton_raphson(self) -> 'float':
        '''float: 'AbsoluteToleranceTranslationalVelocityForNewtonRaphson' is the original name of this property.'''

        return self.wrapped.AbsoluteToleranceTranslationalVelocityForNewtonRaphson

    @absolute_tolerance_translational_velocity_for_newton_raphson.setter
    def absolute_tolerance_translational_velocity_for_newton_raphson(self, value: 'float'):
        self.wrapped.AbsoluteToleranceTranslationalVelocityForNewtonRaphson = float(value) if value else 0.0

    @property
    def absolute_tolerance_lagrange_force_for_newton_raphson(self) -> 'float':
        '''float: 'AbsoluteToleranceLagrangeForceForNewtonRaphson' is the original name of this property.'''

        return self.wrapped.AbsoluteToleranceLagrangeForceForNewtonRaphson

    @absolute_tolerance_lagrange_force_for_newton_raphson.setter
    def absolute_tolerance_lagrange_force_for_newton_raphson(self, value: 'float'):
        self.wrapped.AbsoluteToleranceLagrangeForceForNewtonRaphson = float(value) if value else 0.0

    @property
    def absolute_tolerance_lagrange_moment_for_newton_raphson(self) -> 'float':
        '''float: 'AbsoluteToleranceLagrangeMomentForNewtonRaphson' is the original name of this property.'''

        return self.wrapped.AbsoluteToleranceLagrangeMomentForNewtonRaphson

    @absolute_tolerance_lagrange_moment_for_newton_raphson.setter
    def absolute_tolerance_lagrange_moment_for_newton_raphson(self, value: 'float'):
        self.wrapped.AbsoluteToleranceLagrangeMomentForNewtonRaphson = float(value) if value else 0.0

    @property
    def absolute_tolerance_temperature_for_newton_raphson(self) -> 'float':
        '''float: 'AbsoluteToleranceTemperatureForNewtonRaphson' is the original name of this property.'''

        return self.wrapped.AbsoluteToleranceTemperatureForNewtonRaphson

    @absolute_tolerance_temperature_for_newton_raphson.setter
    def absolute_tolerance_temperature_for_newton_raphson(self, value: 'float'):
        self.wrapped.AbsoluteToleranceTemperatureForNewtonRaphson = float(value) if value else 0.0

    @property
    def relative_tolerance_for_newton_raphson(self) -> 'float':
        '''float: 'RelativeToleranceForNewtonRaphson' is the original name of this property.'''

        return self.wrapped.RelativeToleranceForNewtonRaphson

    @relative_tolerance_for_newton_raphson.setter
    def relative_tolerance_for_newton_raphson(self, value: 'float'):
        self.wrapped.RelativeToleranceForNewtonRaphson = float(value) if value else 0.0

    @property
    def residual_force_tolerance_for_newton_raphson(self) -> 'float':
        '''float: 'ResidualForceToleranceForNewtonRaphson' is the original name of this property.'''

        return self.wrapped.ResidualForceToleranceForNewtonRaphson

    @residual_force_tolerance_for_newton_raphson.setter
    def residual_force_tolerance_for_newton_raphson(self, value: 'float'):
        self.wrapped.ResidualForceToleranceForNewtonRaphson = float(value) if value else 0.0

    @property
    def residual_moment_tolerance_for_newton_raphson(self) -> 'float':
        '''float: 'ResidualMomentToleranceForNewtonRaphson' is the original name of this property.'''

        return self.wrapped.ResidualMomentToleranceForNewtonRaphson

    @residual_moment_tolerance_for_newton_raphson.setter
    def residual_moment_tolerance_for_newton_raphson(self, value: 'float'):
        self.wrapped.ResidualMomentToleranceForNewtonRaphson = float(value) if value else 0.0

    @property
    def residual_lagrange_translational_tolerance_for_newton_raphson(self) -> 'float':
        '''float: 'ResidualLagrangeTranslationalToleranceForNewtonRaphson' is the original name of this property.'''

        return self.wrapped.ResidualLagrangeTranslationalToleranceForNewtonRaphson

    @residual_lagrange_translational_tolerance_for_newton_raphson.setter
    def residual_lagrange_translational_tolerance_for_newton_raphson(self, value: 'float'):
        self.wrapped.ResidualLagrangeTranslationalToleranceForNewtonRaphson = float(value) if value else 0.0

    @property
    def residual_lagrange_angular_tolerance_for_newton_raphson(self) -> 'float':
        '''float: 'ResidualLagrangeAngularToleranceForNewtonRaphson' is the original name of this property.'''

        return self.wrapped.ResidualLagrangeAngularToleranceForNewtonRaphson

    @residual_lagrange_angular_tolerance_for_newton_raphson.setter
    def residual_lagrange_angular_tolerance_for_newton_raphson(self, value: 'float'):
        self.wrapped.ResidualLagrangeAngularToleranceForNewtonRaphson = float(value) if value else 0.0

    @property
    def residual_relative_tolerance_for_newton_raphson(self) -> 'float':
        '''float: 'ResidualRelativeToleranceForNewtonRaphson' is the original name of this property.'''

        return self.wrapped.ResidualRelativeToleranceForNewtonRaphson

    @residual_relative_tolerance_for_newton_raphson.setter
    def residual_relative_tolerance_for_newton_raphson(self, value: 'float'):
        self.wrapped.ResidualRelativeToleranceForNewtonRaphson = float(value) if value else 0.0

    @property
    def residual_temperature_tolerance_for_newton_raphson(self) -> 'float':
        '''float: 'ResidualTemperatureToleranceForNewtonRaphson' is the original name of this property.'''

        return self.wrapped.ResidualTemperatureToleranceForNewtonRaphson

    @residual_temperature_tolerance_for_newton_raphson.setter
    def residual_temperature_tolerance_for_newton_raphson(self, value: 'float'):
        self.wrapped.ResidualTemperatureToleranceForNewtonRaphson = float(value) if value else 0.0

    @property
    def absolute_tolerance_simple(self) -> 'float':
        '''float: 'AbsoluteToleranceSimple' is the original name of this property.'''

        return self.wrapped.AbsoluteToleranceSimple

    @absolute_tolerance_simple.setter
    def absolute_tolerance_simple(self, value: 'float'):
        self.wrapped.AbsoluteToleranceSimple = float(value) if value else 0.0

    @property
    def relative_tolerance_simple(self) -> 'float':
        '''float: 'RelativeToleranceSimple' is the original name of this property.'''

        return self.wrapped.RelativeToleranceSimple

    @relative_tolerance_simple.setter
    def relative_tolerance_simple(self, value: 'float'):
        self.wrapped.RelativeToleranceSimple = float(value) if value else 0.0

    @property
    def rayleigh_damping_alpha(self) -> 'float':
        '''float: 'RayleighDampingAlpha' is the original name of this property.'''

        return self.wrapped.RayleighDampingAlpha

    @rayleigh_damping_alpha.setter
    def rayleigh_damping_alpha(self, value: 'float'):
        self.wrapped.RayleighDampingAlpha = float(value) if value else 0.0

    @property
    def rayleigh_damping_beta(self) -> 'float':
        '''float: 'RayleighDampingBeta' is the original name of this property.'''

        return self.wrapped.RayleighDampingBeta

    @rayleigh_damping_beta.setter
    def rayleigh_damping_beta(self, value: 'float'):
        self.wrapped.RayleighDampingBeta = float(value) if value else 0.0

    @property
    def damping_scaling_for_initial_transients(self) -> '_53.DampingScalingTypeForInitialTransients':
        '''DampingScalingTypeForInitialTransients: 'DampingScalingForInitialTransients' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.DampingScalingForInitialTransients)
        return constructor.new(_53.DampingScalingTypeForInitialTransients)(value) if value is not None else None

    @damping_scaling_for_initial_transients.setter
    def damping_scaling_for_initial_transients(self, value: '_53.DampingScalingTypeForInitialTransients'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.DampingScalingForInitialTransients = value

    @property
    def damping_scaling_factor(self) -> 'float':
        '''float: 'DampingScalingFactor' is the original name of this property.'''

        return self.wrapped.DampingScalingFactor

    @damping_scaling_factor.setter
    def damping_scaling_factor(self, value: 'float'):
        self.wrapped.DampingScalingFactor = float(value) if value else 0.0

    @property
    def time_for_initial_transients(self) -> 'float':
        '''float: 'TimeForInitialTransients' is the original name of this property.'''

        return self.wrapped.TimeForInitialTransients

    @time_for_initial_transients.setter
    def time_for_initial_transients(self, value: 'float'):
        self.wrapped.TimeForInitialTransients = float(value) if value else 0.0

    @property
    def log_initial_transients(self) -> 'bool':
        '''bool: 'LogInitialTransients' is the original name of this property.'''

        return self.wrapped.LogInitialTransients

    @log_initial_transients.setter
    def log_initial_transients(self, value: 'bool'):
        self.wrapped.LogInitialTransients = bool(value) if value else False

    @property
    def limit_time_step_for_final_results(self) -> 'bool':
        '''bool: 'LimitTimeStepForFinalResults' is the original name of this property.'''

        return self.wrapped.LimitTimeStepForFinalResults

    @limit_time_step_for_final_results.setter
    def limit_time_step_for_final_results(self, value: 'bool'):
        self.wrapped.LimitTimeStepForFinalResults = bool(value) if value else False

    @property
    def maximum_time_step_for_final_results(self) -> 'float':
        '''float: 'MaximumTimeStepForFinalResults' is the original name of this property.'''

        return self.wrapped.MaximumTimeStepForFinalResults

    @maximum_time_step_for_final_results.setter
    def maximum_time_step_for_final_results(self, value: 'float'):
        self.wrapped.MaximumTimeStepForFinalResults = float(value) if value else 0.0

    @property
    def time_to_start_using_final_results_maximum_time_step(self) -> 'float':
        '''float: 'TimeToStartUsingFinalResultsMaximumTimeStep' is the original name of this property.'''

        return self.wrapped.TimeToStartUsingFinalResultsMaximumTimeStep

    @time_to_start_using_final_results_maximum_time_step.setter
    def time_to_start_using_final_results_maximum_time_step(self, value: 'float'):
        self.wrapped.TimeToStartUsingFinalResultsMaximumTimeStep = float(value) if value else 0.0

    @property
    def result_logging_frequency(self) -> '_78.ResultLoggingFrequency':
        '''ResultLoggingFrequency: 'ResultLoggingFrequency' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ResultLoggingFrequency)
        return constructor.new(_78.ResultLoggingFrequency)(value) if value is not None else None

    @result_logging_frequency.setter
    def result_logging_frequency(self, value: '_78.ResultLoggingFrequency'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ResultLoggingFrequency = value

    @property
    def minimum_step_between_results(self) -> 'float':
        '''float: 'MinimumStepBetweenResults' is the original name of this property.'''

        return self.wrapped.MinimumStepBetweenResults

    @minimum_step_between_results.setter
    def minimum_step_between_results(self, value: 'float'):
        self.wrapped.MinimumStepBetweenResults = float(value) if value else 0.0
