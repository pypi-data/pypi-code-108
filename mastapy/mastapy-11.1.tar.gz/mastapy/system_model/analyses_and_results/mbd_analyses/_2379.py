'''_2379.py

MultibodyDynamicsAnalysis
'''


from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.mbd_analyses import _5187
from mastapy.nodal_analysis.system_solvers import (
    _113, _95, _96, _99,
    _100, _101, _102, _103,
    _104, _105, _106, _111,
    _114
)
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.analysis_cases import _7268
from mastapy._internal.python_net import python_net_import

_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'MultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('MultibodyDynamicsAnalysis',)


class MultibodyDynamicsAnalysis(_7268.TimeSeriesLoadAnalysisCase):
    '''MultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def percentage_time_spent_in_masta_solver(self) -> 'float':
        '''float: 'PercentageTimeSpentInMASTASolver' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PercentageTimeSpentInMASTASolver

    @property
    def has_interface_analysis_results_available(self) -> 'bool':
        '''bool: 'HasInterfaceAnalysisResultsAvailable' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HasInterfaceAnalysisResultsAvailable

    @property
    def mbd_options(self) -> '_5187.MBDAnalysisOptions':
        '''MBDAnalysisOptions: 'MBDOptions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5187.MBDAnalysisOptions)(self.wrapped.MBDOptions) if self.wrapped.MBDOptions is not None else None

    @property
    def transient_solver(self) -> '_113.TransientSolver':
        '''TransientSolver: 'TransientSolver' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _113.TransientSolver.TYPE not in self.wrapped.TransientSolver.__class__.__mro__:
            raise CastException('Failed to cast transient_solver to TransientSolver. Expected: {}.'.format(self.wrapped.TransientSolver.__class__.__qualname__))

        return constructor.new_override(self.wrapped.TransientSolver.__class__)(self.wrapped.TransientSolver) if self.wrapped.TransientSolver is not None else None

    @property
    def transient_solver_of_type_backward_euler_acceleration_step_halving_transient_solver(self) -> '_95.BackwardEulerAccelerationStepHalvingTransientSolver':
        '''BackwardEulerAccelerationStepHalvingTransientSolver: 'TransientSolver' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _95.BackwardEulerAccelerationStepHalvingTransientSolver.TYPE not in self.wrapped.TransientSolver.__class__.__mro__:
            raise CastException('Failed to cast transient_solver to BackwardEulerAccelerationStepHalvingTransientSolver. Expected: {}.'.format(self.wrapped.TransientSolver.__class__.__qualname__))

        return constructor.new_override(self.wrapped.TransientSolver.__class__)(self.wrapped.TransientSolver) if self.wrapped.TransientSolver is not None else None

    @property
    def transient_solver_of_type_backward_euler_transient_solver(self) -> '_96.BackwardEulerTransientSolver':
        '''BackwardEulerTransientSolver: 'TransientSolver' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _96.BackwardEulerTransientSolver.TYPE not in self.wrapped.TransientSolver.__class__.__mro__:
            raise CastException('Failed to cast transient_solver to BackwardEulerTransientSolver. Expected: {}.'.format(self.wrapped.TransientSolver.__class__.__qualname__))

        return constructor.new_override(self.wrapped.TransientSolver.__class__)(self.wrapped.TransientSolver) if self.wrapped.TransientSolver is not None else None

    @property
    def transient_solver_of_type_internal_transient_solver(self) -> '_99.InternalTransientSolver':
        '''InternalTransientSolver: 'TransientSolver' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _99.InternalTransientSolver.TYPE not in self.wrapped.TransientSolver.__class__.__mro__:
            raise CastException('Failed to cast transient_solver to InternalTransientSolver. Expected: {}.'.format(self.wrapped.TransientSolver.__class__.__qualname__))

        return constructor.new_override(self.wrapped.TransientSolver.__class__)(self.wrapped.TransientSolver) if self.wrapped.TransientSolver is not None else None

    @property
    def transient_solver_of_type_lobatto_iiia_transient_solver(self) -> '_100.LobattoIIIATransientSolver':
        '''LobattoIIIATransientSolver: 'TransientSolver' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _100.LobattoIIIATransientSolver.TYPE not in self.wrapped.TransientSolver.__class__.__mro__:
            raise CastException('Failed to cast transient_solver to LobattoIIIATransientSolver. Expected: {}.'.format(self.wrapped.TransientSolver.__class__.__qualname__))

        return constructor.new_override(self.wrapped.TransientSolver.__class__)(self.wrapped.TransientSolver) if self.wrapped.TransientSolver is not None else None

    @property
    def transient_solver_of_type_lobatto_iiic_transient_solver(self) -> '_101.LobattoIIICTransientSolver':
        '''LobattoIIICTransientSolver: 'TransientSolver' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _101.LobattoIIICTransientSolver.TYPE not in self.wrapped.TransientSolver.__class__.__mro__:
            raise CastException('Failed to cast transient_solver to LobattoIIICTransientSolver. Expected: {}.'.format(self.wrapped.TransientSolver.__class__.__qualname__))

        return constructor.new_override(self.wrapped.TransientSolver.__class__)(self.wrapped.TransientSolver) if self.wrapped.TransientSolver is not None else None

    @property
    def transient_solver_of_type_newmark_acceleration_transient_solver(self) -> '_102.NewmarkAccelerationTransientSolver':
        '''NewmarkAccelerationTransientSolver: 'TransientSolver' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _102.NewmarkAccelerationTransientSolver.TYPE not in self.wrapped.TransientSolver.__class__.__mro__:
            raise CastException('Failed to cast transient_solver to NewmarkAccelerationTransientSolver. Expected: {}.'.format(self.wrapped.TransientSolver.__class__.__qualname__))

        return constructor.new_override(self.wrapped.TransientSolver.__class__)(self.wrapped.TransientSolver) if self.wrapped.TransientSolver is not None else None

    @property
    def transient_solver_of_type_newmark_transient_solver(self) -> '_103.NewmarkTransientSolver':
        '''NewmarkTransientSolver: 'TransientSolver' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _103.NewmarkTransientSolver.TYPE not in self.wrapped.TransientSolver.__class__.__mro__:
            raise CastException('Failed to cast transient_solver to NewmarkTransientSolver. Expected: {}.'.format(self.wrapped.TransientSolver.__class__.__qualname__))

        return constructor.new_override(self.wrapped.TransientSolver.__class__)(self.wrapped.TransientSolver) if self.wrapped.TransientSolver is not None else None

    @property
    def transient_solver_of_type_semi_implicit_transient_solver(self) -> '_104.SemiImplicitTransientSolver':
        '''SemiImplicitTransientSolver: 'TransientSolver' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _104.SemiImplicitTransientSolver.TYPE not in self.wrapped.TransientSolver.__class__.__mro__:
            raise CastException('Failed to cast transient_solver to SemiImplicitTransientSolver. Expected: {}.'.format(self.wrapped.TransientSolver.__class__.__qualname__))

        return constructor.new_override(self.wrapped.TransientSolver.__class__)(self.wrapped.TransientSolver) if self.wrapped.TransientSolver is not None else None

    @property
    def transient_solver_of_type_simple_acceleration_based_step_halving_transient_solver(self) -> '_105.SimpleAccelerationBasedStepHalvingTransientSolver':
        '''SimpleAccelerationBasedStepHalvingTransientSolver: 'TransientSolver' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _105.SimpleAccelerationBasedStepHalvingTransientSolver.TYPE not in self.wrapped.TransientSolver.__class__.__mro__:
            raise CastException('Failed to cast transient_solver to SimpleAccelerationBasedStepHalvingTransientSolver. Expected: {}.'.format(self.wrapped.TransientSolver.__class__.__qualname__))

        return constructor.new_override(self.wrapped.TransientSolver.__class__)(self.wrapped.TransientSolver) if self.wrapped.TransientSolver is not None else None

    @property
    def transient_solver_of_type_simple_velocity_based_step_halving_transient_solver(self) -> '_106.SimpleVelocityBasedStepHalvingTransientSolver':
        '''SimpleVelocityBasedStepHalvingTransientSolver: 'TransientSolver' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _106.SimpleVelocityBasedStepHalvingTransientSolver.TYPE not in self.wrapped.TransientSolver.__class__.__mro__:
            raise CastException('Failed to cast transient_solver to SimpleVelocityBasedStepHalvingTransientSolver. Expected: {}.'.format(self.wrapped.TransientSolver.__class__.__qualname__))

        return constructor.new_override(self.wrapped.TransientSolver.__class__)(self.wrapped.TransientSolver) if self.wrapped.TransientSolver is not None else None

    @property
    def transient_solver_of_type_step_halving_transient_solver(self) -> '_111.StepHalvingTransientSolver':
        '''StepHalvingTransientSolver: 'TransientSolver' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _111.StepHalvingTransientSolver.TYPE not in self.wrapped.TransientSolver.__class__.__mro__:
            raise CastException('Failed to cast transient_solver to StepHalvingTransientSolver. Expected: {}.'.format(self.wrapped.TransientSolver.__class__.__qualname__))

        return constructor.new_override(self.wrapped.TransientSolver.__class__)(self.wrapped.TransientSolver) if self.wrapped.TransientSolver is not None else None

    @property
    def transient_solver_of_type_wilson_theta_transient_solver(self) -> '_114.WilsonThetaTransientSolver':
        '''WilsonThetaTransientSolver: 'TransientSolver' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _114.WilsonThetaTransientSolver.TYPE not in self.wrapped.TransientSolver.__class__.__mro__:
            raise CastException('Failed to cast transient_solver to WilsonThetaTransientSolver. Expected: {}.'.format(self.wrapped.TransientSolver.__class__.__qualname__))

        return constructor.new_override(self.wrapped.TransientSolver.__class__)(self.wrapped.TransientSolver) if self.wrapped.TransientSolver is not None else None
