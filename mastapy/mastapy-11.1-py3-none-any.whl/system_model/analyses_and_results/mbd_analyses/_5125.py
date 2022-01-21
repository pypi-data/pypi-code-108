'''_5125.py

ClutchConnectionMultibodyDynamicsAnalysis
'''


from mastapy._internal import constructor
from mastapy.system_model.connections_and_sockets.couplings import _2084
from mastapy.system_model.analyses_and_results.static_loads import _6547
from mastapy.system_model.analyses_and_results.mbd_analyses import _5142
from mastapy._internal.python_net import python_net_import

_CLUTCH_CONNECTION_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'ClutchConnectionMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ClutchConnectionMultibodyDynamicsAnalysis',)


class ClutchConnectionMultibodyDynamicsAnalysis(_5142.CouplingConnectionMultibodyDynamicsAnalysis):
    '''ClutchConnectionMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _CLUTCH_CONNECTION_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ClutchConnectionMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def is_locked(self) -> 'bool':
        '''bool: 'IsLocked' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IsLocked

    @property
    def clutch_connection_viscous_torque(self) -> 'float':
        '''float: 'ClutchConnectionViscousTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ClutchConnectionViscousTorque

    @property
    def clutch_connection_elastic_torque(self) -> 'float':
        '''float: 'ClutchConnectionElasticTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ClutchConnectionElasticTorque

    @property
    def clutch_torque_capacity(self) -> 'float':
        '''float: 'ClutchTorqueCapacity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ClutchTorqueCapacity

    @property
    def percentage_applied_pressure(self) -> 'float':
        '''float: 'PercentageAppliedPressure' is the original name of this property.'''

        return self.wrapped.PercentageAppliedPressure

    @percentage_applied_pressure.setter
    def percentage_applied_pressure(self, value: 'float'):
        self.wrapped.PercentageAppliedPressure = float(value) if value else 0.0

    @property
    def applied_clutch_pressure_at_piston(self) -> 'float':
        '''float: 'AppliedClutchPressureAtPiston' is the original name of this property.'''

        return self.wrapped.AppliedClutchPressureAtPiston

    @applied_clutch_pressure_at_piston.setter
    def applied_clutch_pressure_at_piston(self, value: 'float'):
        self.wrapped.AppliedClutchPressureAtPiston = float(value) if value else 0.0

    @property
    def applied_clutch_pressure_at_clutch_plate(self) -> 'float':
        '''float: 'AppliedClutchPressureAtClutchPlate' is the original name of this property.'''

        return self.wrapped.AppliedClutchPressureAtClutchPlate

    @applied_clutch_pressure_at_clutch_plate.setter
    def applied_clutch_pressure_at_clutch_plate(self, value: 'float'):
        self.wrapped.AppliedClutchPressureAtClutchPlate = float(value) if value else 0.0

    @property
    def relative_shaft_speed(self) -> 'float':
        '''float: 'RelativeShaftSpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeShaftSpeed

    @property
    def relative_shaft_displacement(self) -> 'float':
        '''float: 'RelativeShaftDisplacement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeShaftDisplacement

    @property
    def excess_clutch_torque_capacity(self) -> 'float':
        '''float: 'ExcessClutchTorqueCapacity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ExcessClutchTorqueCapacity

    @property
    def clutch_plate_dynamic_temperature(self) -> 'float':
        '''float: 'ClutchPlateDynamicTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ClutchPlateDynamicTemperature

    @property
    def power_loss(self) -> 'float':
        '''float: 'PowerLoss' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PowerLoss

    @property
    def connection_design(self) -> '_2084.ClutchConnection':
        '''ClutchConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2084.ClutchConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def connection_load_case(self) -> '_6547.ClutchConnectionLoadCase':
        '''ClutchConnectionLoadCase: 'ConnectionLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6547.ClutchConnectionLoadCase)(self.wrapped.ConnectionLoadCase) if self.wrapped.ConnectionLoadCase is not None else None
