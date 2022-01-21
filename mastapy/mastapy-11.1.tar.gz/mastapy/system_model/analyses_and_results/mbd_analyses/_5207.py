'''_5207.py

RootAssemblyMultibodyDynamicsAnalysis
'''


from mastapy._internal import constructor
from mastapy.system_model.part_model import _2215
from mastapy.system_model.analyses_and_results.mbd_analyses import _2379, _5110
from mastapy._internal.python_net import python_net_import

_ROOT_ASSEMBLY_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'RootAssemblyMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('RootAssemblyMultibodyDynamicsAnalysis',)


class RootAssemblyMultibodyDynamicsAnalysis(_5110.AssemblyMultibodyDynamicsAnalysis):
    '''RootAssemblyMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _ROOT_ASSEMBLY_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RootAssemblyMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def log_10_time_step(self) -> 'float':
        '''float: 'Log10TimeStep' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Log10TimeStep

    @property
    def actual_torque_ratio(self) -> 'float':
        '''float: 'ActualTorqueRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ActualTorqueRatio

    @property
    def actual_torque_ratio_turbine_to_output(self) -> 'float':
        '''float: 'ActualTorqueRatioTurbineToOutput' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ActualTorqueRatioTurbineToOutput

    @property
    def power_loss(self) -> 'float':
        '''float: 'PowerLoss' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PowerLoss

    @property
    def efficiency(self) -> 'float':
        '''float: 'Efficiency' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Efficiency

    @property
    def input_power(self) -> 'float':
        '''float: 'InputPower' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InputPower

    @property
    def input_energy(self) -> 'float':
        '''float: 'InputEnergy' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InputEnergy

    @property
    def energy_lost(self) -> 'float':
        '''float: 'EnergyLost' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EnergyLost

    @property
    def overall_efficiency(self) -> 'float':
        '''float: 'OverallEfficiency' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OverallEfficiency

    @property
    def vehicle_position(self) -> 'float':
        '''float: 'VehiclePosition' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VehiclePosition

    @property
    def vehicle_speed(self) -> 'float':
        '''float: 'VehicleSpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VehicleSpeed

    @property
    def vehicle_drag(self) -> 'float':
        '''float: 'VehicleDrag' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VehicleDrag

    @property
    def vehicle_acceleration(self) -> 'float':
        '''float: 'VehicleAcceleration' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VehicleAcceleration

    @property
    def brake_force(self) -> 'float':
        '''float: 'BrakeForce' is the original name of this property.'''

        return self.wrapped.BrakeForce

    @brake_force.setter
    def brake_force(self, value: 'float'):
        self.wrapped.BrakeForce = float(value) if value else 0.0

    @property
    def road_incline(self) -> 'float':
        '''float: 'RoadIncline' is the original name of this property.'''

        return self.wrapped.RoadIncline

    @road_incline.setter
    def road_incline(self, value: 'float'):
        self.wrapped.RoadIncline = float(value) if value else 0.0

    @property
    def force_from_road_incline(self) -> 'float':
        '''float: 'ForceFromRoadIncline' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ForceFromRoadIncline

    @property
    def force_from_wheels(self) -> 'float':
        '''float: 'ForceFromWheels' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ForceFromWheels

    @property
    def total_force_on_vehicle(self) -> 'float':
        '''float: 'TotalForceOnVehicle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalForceOnVehicle

    @property
    def maximum_vehicle_speed_error(self) -> 'float':
        '''float: 'MaximumVehicleSpeedError' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumVehicleSpeedError

    @property
    def vehicle_speed_drive_cycle_error(self) -> 'float':
        '''float: 'VehicleSpeedDriveCycleError' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VehicleSpeedDriveCycleError

    @property
    def percentage_error_in_vehicle_speed_compared_to_drive_cycle(self) -> 'float':
        '''float: 'PercentageErrorInVehicleSpeedComparedToDriveCycle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PercentageErrorInVehicleSpeedComparedToDriveCycle

    @property
    def current_target_vehicle_speed(self) -> 'float':
        '''float: 'CurrentTargetVehicleSpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CurrentTargetVehicleSpeed

    @property
    def oil_dynamic_temperature(self) -> 'float':
        '''float: 'OilDynamicTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OilDynamicTemperature

    @property
    def assembly_design(self) -> '_2215.RootAssembly':
        '''RootAssembly: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2215.RootAssembly)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def multibody_dynamics_analysis_inputs(self) -> '_2379.MultibodyDynamicsAnalysis':
        '''MultibodyDynamicsAnalysis: 'MultibodyDynamicsAnalysisInputs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2379.MultibodyDynamicsAnalysis)(self.wrapped.MultibodyDynamicsAnalysisInputs) if self.wrapped.MultibodyDynamicsAnalysisInputs is not None else None
