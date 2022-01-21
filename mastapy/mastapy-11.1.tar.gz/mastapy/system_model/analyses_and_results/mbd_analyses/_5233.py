'''_5233.py

TorqueConverterConnectionMultibodyDynamicsAnalysis
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.system_model.analyses_and_results.mbd_analyses import _5237, _5142
from mastapy.system_model.connections_and_sockets.couplings import _2094
from mastapy.system_model.analyses_and_results.static_loads import _6691
from mastapy._internal.python_net import python_net_import

_TORQUE_CONVERTER_CONNECTION_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'TorqueConverterConnectionMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('TorqueConverterConnectionMultibodyDynamicsAnalysis',)


class TorqueConverterConnectionMultibodyDynamicsAnalysis(_5142.CouplingConnectionMultibodyDynamicsAnalysis):
    '''TorqueConverterConnectionMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _TORQUE_CONVERTER_CONNECTION_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TorqueConverterConnectionMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def pump_torque(self) -> 'float':
        '''float: 'PumpTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PumpTorque

    @property
    def turbine_torque(self) -> 'float':
        '''float: 'TurbineTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TurbineTorque

    @property
    def speed_ratio(self) -> 'float':
        '''float: 'SpeedRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SpeedRatio

    @property
    def torque_ratio(self) -> 'float':
        '''float: 'TorqueRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TorqueRatio

    @property
    def capacity_factor_k(self) -> 'float':
        '''float: 'CapacityFactorK' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CapacityFactorK

    @property
    def inverse_capacity_factor_1k(self) -> 'float':
        '''float: 'InverseCapacityFactor1K' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InverseCapacityFactor1K

    @property
    def locked_torque(self) -> 'float':
        '''float: 'LockedTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LockedTorque

    @property
    def lock_up_viscous_torque(self) -> 'float':
        '''float: 'LockUpViscousTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LockUpViscousTorque

    @property
    def is_locked(self) -> 'bool':
        '''bool: 'IsLocked' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IsLocked

    @property
    def percentage_applied_pressure(self) -> 'float':
        '''float: 'PercentageAppliedPressure' is the original name of this property.'''

        return self.wrapped.PercentageAppliedPressure

    @percentage_applied_pressure.setter
    def percentage_applied_pressure(self, value: 'float'):
        self.wrapped.PercentageAppliedPressure = float(value) if value else 0.0

    @property
    def locking_status(self) -> '_5237.TorqueConverterStatus':
        '''TorqueConverterStatus: 'LockingStatus' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.LockingStatus)
        return constructor.new(_5237.TorqueConverterStatus)(value) if value is not None else None

    @property
    def lock_up_clutch_temperature(self) -> 'float':
        '''float: 'LockUpClutchTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LockUpClutchTemperature

    @property
    def power_loss(self) -> 'float':
        '''float: 'PowerLoss' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PowerLoss

    @property
    def connection_design(self) -> '_2094.TorqueConverterConnection':
        '''TorqueConverterConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2094.TorqueConverterConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def connection_load_case(self) -> '_6691.TorqueConverterConnectionLoadCase':
        '''TorqueConverterConnectionLoadCase: 'ConnectionLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6691.TorqueConverterConnectionLoadCase)(self.wrapped.ConnectionLoadCase) if self.wrapped.ConnectionLoadCase is not None else None
