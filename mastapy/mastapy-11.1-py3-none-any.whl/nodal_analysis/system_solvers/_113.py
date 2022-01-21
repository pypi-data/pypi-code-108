'''_113.py

TransientSolver
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.nodal_analysis import _84
from mastapy.nodal_analysis.system_solvers import _98
from mastapy._internal.python_net import python_net_import

_TRANSIENT_SOLVER = python_net_import('SMT.MastaAPI.NodalAnalysis.SystemSolvers', 'TransientSolver')


__docformat__ = 'restructuredtext en'
__all__ = ('TransientSolver',)


class TransientSolver(_98.DynamicSolver):
    '''TransientSolver

    This is a mastapy class.
    '''

    TYPE = _TRANSIENT_SOLVER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TransientSolver.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def number_of_time_steps_taken(self) -> 'int':
        '''int: 'NumberOfTimeStepsTaken' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfTimeStepsTaken

    @property
    def number_of_failed_time_steps(self) -> 'int':
        '''int: 'NumberOfFailedTimeSteps' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfFailedTimeSteps

    @property
    def number_of_failed_time_steps_at_minimum_time_step(self) -> 'int':
        '''int: 'NumberOfFailedTimeStepsAtMinimumTimeStep' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfFailedTimeStepsAtMinimumTimeStep

    @property
    def number_of_times_step_error_tolerance_not_met(self) -> 'int':
        '''int: 'NumberOfTimesStepErrorToleranceNotMet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfTimesStepErrorToleranceNotMet

    @property
    def number_of_failed_newton_raphson_solves(self) -> 'int':
        '''int: 'NumberOfFailedNewtonRaphsonSolves' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfFailedNewtonRaphsonSolves

    @property
    def number_of_newton_raphson_solves(self) -> 'int':
        '''int: 'NumberOfNewtonRaphsonSolves' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfNewtonRaphsonSolves

    @property
    def number_of_newton_raphson_jacobian_evaluations(self) -> 'int':
        '''int: 'NumberOfNewtonRaphsonJacobianEvaluations' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfNewtonRaphsonJacobianEvaluations

    @property
    def number_of_newton_raphson_residual_evaluations(self) -> 'int':
        '''int: 'NumberOfNewtonRaphsonResidualEvaluations' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfNewtonRaphsonResidualEvaluations

    @property
    def number_of_newton_raphson_values_not_changing(self) -> 'int':
        '''int: 'NumberOfNewtonRaphsonValuesNotChanging' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfNewtonRaphsonValuesNotChanging

    @property
    def number_of_newton_raphson_residual_tolerance_met(self) -> 'int':
        '''int: 'NumberOfNewtonRaphsonResidualToleranceMet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfNewtonRaphsonResidualToleranceMet

    @property
    def number_of_newton_raphson_maximum_iterations_reached(self) -> 'int':
        '''int: 'NumberOfNewtonRaphsonMaximumIterationsReached' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfNewtonRaphsonMaximumIterationsReached

    @property
    def number_of_newton_raphson_other_status_results(self) -> 'int':
        '''int: 'NumberOfNewtonRaphsonOtherStatusResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfNewtonRaphsonOtherStatusResults

    @property
    def average_number_of_jacobian_evaluations_per_newton_raphson_solve(self) -> 'float':
        '''float: 'AverageNumberOfJacobianEvaluationsPerNewtonRaphsonSolve' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageNumberOfJacobianEvaluationsPerNewtonRaphsonSolve

    @property
    def solver_status(self) -> '_84.TransientSolverStatus':
        '''TransientSolverStatus: 'SolverStatus' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.SolverStatus)
        return constructor.new(_84.TransientSolverStatus)(value) if value is not None else None

    @solver_status.setter
    def solver_status(self, value: '_84.TransientSolverStatus'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.SolverStatus = value

    @property
    def number_of_interface_time_steps(self) -> 'int':
        '''int: 'NumberOfInterfaceTimeSteps' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfInterfaceTimeSteps

    @property
    def interface_analysis_time(self) -> 'float':
        '''float: 'InterfaceAnalysisTime' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InterfaceAnalysisTime

    def times_of_logged_results(self) -> 'List[float]':
        ''' 'TimesOfLoggedResults' is the original name of this method.

        Returns:
            List[float]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.TimesOfLoggedResults(), float)
