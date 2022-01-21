'''_5200.py

PowerLoadMultibodyDynamicsAnalysis
'''


from mastapy._internal import constructor
from mastapy.system_model.part_model import _2213
from mastapy.system_model.analyses_and_results.static_loads import _6657
from mastapy.system_model.analyses_and_results.mbd_analyses import _5240
from mastapy._internal.python_net import python_net_import

_POWER_LOAD_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'PowerLoadMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('PowerLoadMultibodyDynamicsAnalysis',)


class PowerLoadMultibodyDynamicsAnalysis(_5240.VirtualComponentMultibodyDynamicsAnalysis):
    '''PowerLoadMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _POWER_LOAD_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PowerLoadMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def angular_jerk_rate_of_change_of_acceleration(self) -> 'float':
        '''float: 'AngularJerkRateOfChangeOfAcceleration' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AngularJerkRateOfChangeOfAcceleration

    @property
    def energy_input(self) -> 'float':
        '''float: 'EnergyInput' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EnergyInput

    @property
    def fuel_consumption_instantaneous(self) -> 'float':
        '''float: 'FuelConsumptionInstantaneous' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FuelConsumptionInstantaneous

    @property
    def total_fuel_consumed(self) -> 'float':
        '''float: 'TotalFuelConsumed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalFuelConsumed

    @property
    def controller_torque(self) -> 'float':
        '''float: 'ControllerTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ControllerTorque

    @property
    def unfiltered_controller_torque(self) -> 'float':
        '''float: 'UnfilteredControllerTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.UnfilteredControllerTorque

    @property
    def filtered_engine_throttle(self) -> 'float':
        '''float: 'FilteredEngineThrottle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FilteredEngineThrottle

    @property
    def engine_throttle_position_over_time(self) -> 'float':
        '''float: 'EngineThrottlePositionOverTime' is the original name of this property.'''

        return self.wrapped.EngineThrottlePositionOverTime

    @engine_throttle_position_over_time.setter
    def engine_throttle_position_over_time(self, value: 'float'):
        self.wrapped.EngineThrottlePositionOverTime = float(value) if value else 0.0

    @property
    def engine_throttle_from_interface(self) -> 'float':
        '''float: 'EngineThrottleFromInterface' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EngineThrottleFromInterface

    @property
    def error_in_engine_idle_speed(self) -> 'float':
        '''float: 'ErrorInEngineIdleSpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ErrorInEngineIdleSpeed

    @property
    def engine_idle_speed_control_enabled(self) -> 'bool':
        '''bool: 'EngineIdleSpeedControlEnabled' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EngineIdleSpeedControlEnabled

    @property
    def applied_torque(self) -> 'float':
        '''float: 'AppliedTorque' is the original name of this property.'''

        return self.wrapped.AppliedTorque

    @applied_torque.setter
    def applied_torque(self, value: 'float'):
        self.wrapped.AppliedTorque = float(value) if value else 0.0

    @property
    def interface_input_torque_used_in_solver(self) -> 'float':
        '''float: 'InterfaceInputTorqueUsedInSolver' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InterfaceInputTorqueUsedInSolver

    @property
    def drag_torque(self) -> 'float':
        '''float: 'DragTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DragTorque

    @property
    def elastic_torque(self) -> 'float':
        '''float: 'ElasticTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ElasticTorque

    @property
    def total_torque(self) -> 'float':
        '''float: 'TotalTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalTorque

    @property
    def torque_from_vehicle(self) -> 'float':
        '''float: 'TorqueFromVehicle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TorqueFromVehicle

    @property
    def torque_on_each_wheel(self) -> 'float':
        '''float: 'TorqueOnEachWheel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TorqueOnEachWheel

    @property
    def is_locked(self) -> 'bool':
        '''bool: 'IsLocked' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IsLocked

    @property
    def power(self) -> 'float':
        '''float: 'Power' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Power

    @property
    def is_wheel_using_static_friction(self) -> 'bool':
        '''bool: 'IsWheelUsingStaticFriction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IsWheelUsingStaticFriction

    @property
    def longitudinal_slip_ratio(self) -> 'float':
        '''float: 'LongitudinalSlipRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LongitudinalSlipRatio

    @property
    def current_coefficient_of_friction_with_ground(self) -> 'float':
        '''float: 'CurrentCoefficientOfFrictionWithGround' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CurrentCoefficientOfFrictionWithGround

    @property
    def error_in_target_speed(self) -> 'float':
        '''float: 'ErrorInTargetSpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ErrorInTargetSpeed

    @property
    def component_design(self) -> '_2213.PowerLoad':
        '''PowerLoad: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2213.PowerLoad)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6657.PowerLoadLoadCase':
        '''PowerLoadLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6657.PowerLoadLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
