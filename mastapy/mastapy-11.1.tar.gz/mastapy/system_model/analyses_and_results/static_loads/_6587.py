'''_6587.py

ElectricMachineHarmonicLoadData
'''


from typing import List

from PIL.Image import Image

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy._internal.implicit import enum_with_selected_value, list_with_selected_item
from mastapy.system_model.analyses_and_results.static_loads import _6695, _6621, _6671
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.system_model.fe import _2126
from mastapy.utility_gui.charts import _1625
from mastapy.math_utility import _1312
from mastapy._internal.python_net import python_net_import

_ELECTRIC_MACHINE_HARMONIC_LOAD_DATA = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'ElectricMachineHarmonicLoadData')


__docformat__ = 'restructuredtext en'
__all__ = ('ElectricMachineHarmonicLoadData',)


class ElectricMachineHarmonicLoadData(_6671.SpeedDependentHarmonicLoadData):
    '''ElectricMachineHarmonicLoadData

    This is a mastapy class.
    '''

    TYPE = _ELECTRIC_MACHINE_HARMONIC_LOAD_DATA

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ElectricMachineHarmonicLoadData.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def constant_torque(self) -> 'float':
        '''float: 'ConstantTorque' is the original name of this property.'''

        return self.wrapped.ConstantTorque

    @constant_torque.setter
    def constant_torque(self, value: 'float'):
        self.wrapped.ConstantTorque = float(value) if value else 0.0

    @property
    def torque_ripple_input_type(self) -> 'enum_with_selected_value.EnumWithSelectedValue_TorqueRippleInputType':
        '''enum_with_selected_value.EnumWithSelectedValue_TorqueRippleInputType: 'TorqueRippleInputType' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_TorqueRippleInputType.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.TorqueRippleInputType, value) if self.wrapped.TorqueRippleInputType is not None else None

    @torque_ripple_input_type.setter
    def torque_ripple_input_type(self, value: 'enum_with_selected_value.EnumWithSelectedValue_TorqueRippleInputType.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_TorqueRippleInputType.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.TorqueRippleInputType = value

    @property
    def display_interpolated_data(self) -> 'bool':
        '''bool: 'DisplayInterpolatedData' is the original name of this property.'''

        return self.wrapped.DisplayInterpolatedData

    @display_interpolated_data.setter
    def display_interpolated_data(self, value: 'bool'):
        self.wrapped.DisplayInterpolatedData = bool(value) if value else False

    @property
    def sum_over_all_nodes(self) -> 'bool':
        '''bool: 'SumOverAllNodes' is the original name of this property.'''

        return self.wrapped.SumOverAllNodes

    @sum_over_all_nodes.setter
    def sum_over_all_nodes(self, value: 'bool'):
        self.wrapped.SumOverAllNodes = bool(value) if value else False

    @property
    def stator_radial_loads_amplitude_cut_off(self) -> 'float':
        '''float: 'StatorRadialLoadsAmplitudeCutOff' is the original name of this property.'''

        return self.wrapped.StatorRadialLoadsAmplitudeCutOff

    @stator_radial_loads_amplitude_cut_off.setter
    def stator_radial_loads_amplitude_cut_off(self, value: 'float'):
        self.wrapped.StatorRadialLoadsAmplitudeCutOff = float(value) if value else 0.0

    @property
    def stator_axial_loads_amplitude_cut_off(self) -> 'float':
        '''float: 'StatorAxialLoadsAmplitudeCutOff' is the original name of this property.'''

        return self.wrapped.StatorAxialLoadsAmplitudeCutOff

    @stator_axial_loads_amplitude_cut_off.setter
    def stator_axial_loads_amplitude_cut_off(self, value: 'float'):
        self.wrapped.StatorAxialLoadsAmplitudeCutOff = float(value) if value else 0.0

    @property
    def torque_ripple_amplitude_cut_off(self) -> 'float':
        '''float: 'TorqueRippleAmplitudeCutOff' is the original name of this property.'''

        return self.wrapped.TorqueRippleAmplitudeCutOff

    @torque_ripple_amplitude_cut_off.setter
    def torque_ripple_amplitude_cut_off(self, value: 'float'):
        self.wrapped.TorqueRippleAmplitudeCutOff = float(value) if value else 0.0

    @property
    def rotor_x_force_amplitude_cut_off(self) -> 'float':
        '''float: 'RotorXForceAmplitudeCutOff' is the original name of this property.'''

        return self.wrapped.RotorXForceAmplitudeCutOff

    @rotor_x_force_amplitude_cut_off.setter
    def rotor_x_force_amplitude_cut_off(self, value: 'float'):
        self.wrapped.RotorXForceAmplitudeCutOff = float(value) if value else 0.0

    @property
    def rotor_y_force_amplitude_cut_off(self) -> 'float':
        '''float: 'RotorYForceAmplitudeCutOff' is the original name of this property.'''

        return self.wrapped.RotorYForceAmplitudeCutOff

    @rotor_y_force_amplitude_cut_off.setter
    def rotor_y_force_amplitude_cut_off(self, value: 'float'):
        self.wrapped.RotorYForceAmplitudeCutOff = float(value) if value else 0.0

    @property
    def rotor_z_force_amplitude_cut_off(self) -> 'float':
        '''float: 'RotorZForceAmplitudeCutOff' is the original name of this property.'''

        return self.wrapped.RotorZForceAmplitudeCutOff

    @rotor_z_force_amplitude_cut_off.setter
    def rotor_z_force_amplitude_cut_off(self, value: 'float'):
        self.wrapped.RotorZForceAmplitudeCutOff = float(value) if value else 0.0

    @property
    def rotor_moment_from_stator_teeth_axial_loads_amplitude_cut_off(self) -> 'float':
        '''float: 'RotorMomentFromStatorTeethAxialLoadsAmplitudeCutOff' is the original name of this property.'''

        return self.wrapped.RotorMomentFromStatorTeethAxialLoadsAmplitudeCutOff

    @rotor_moment_from_stator_teeth_axial_loads_amplitude_cut_off.setter
    def rotor_moment_from_stator_teeth_axial_loads_amplitude_cut_off(self, value: 'float'):
        self.wrapped.RotorMomentFromStatorTeethAxialLoadsAmplitudeCutOff = float(value) if value else 0.0

    @property
    def stator_tangential_loads_amplitude_cut_off(self) -> 'float':
        '''float: 'StatorTangentialLoadsAmplitudeCutOff' is the original name of this property.'''

        return self.wrapped.StatorTangentialLoadsAmplitudeCutOff

    @stator_tangential_loads_amplitude_cut_off.setter
    def stator_tangential_loads_amplitude_cut_off(self, value: 'float'):
        self.wrapped.StatorTangentialLoadsAmplitudeCutOff = float(value) if value else 0.0

    @property
    def speed_to_view(self) -> 'float':
        '''float: 'SpeedToView' is the original name of this property.'''

        return self.wrapped.SpeedToView

    @speed_to_view.setter
    def speed_to_view(self, value: 'float'):
        self.wrapped.SpeedToView = float(value) if value else 0.0

    @property
    def show_all_teeth(self) -> 'bool':
        '''bool: 'ShowAllTeeth' is the original name of this property.'''

        return self.wrapped.ShowAllTeeth

    @show_all_teeth.setter
    def show_all_teeth(self, value: 'bool'):
        self.wrapped.ShowAllTeeth = bool(value) if value else False

    @property
    def selected_tooth(self) -> 'list_with_selected_item.ListWithSelectedItem_FESubstructureNode':
        '''list_with_selected_item.ListWithSelectedItem_FESubstructureNode: 'SelectedTooth' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_FESubstructureNode)(self.wrapped.SelectedTooth) if self.wrapped.SelectedTooth is not None else None

    @selected_tooth.setter
    def selected_tooth(self, value: 'list_with_selected_item.ListWithSelectedItem_FESubstructureNode.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_FESubstructureNode.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_FESubstructureNode.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.SelectedTooth = value

    @property
    def compare_torque_ripple_and_stator_torque_reaction_derived_from_stator_tangential_loads(self) -> 'bool':
        '''bool: 'CompareTorqueRippleAndStatorTorqueReactionDerivedFromStatorTangentialLoads' is the original name of this property.'''

        return self.wrapped.CompareTorqueRippleAndStatorTorqueReactionDerivedFromStatorTangentialLoads

    @compare_torque_ripple_and_stator_torque_reaction_derived_from_stator_tangential_loads.setter
    def compare_torque_ripple_and_stator_torque_reaction_derived_from_stator_tangential_loads(self, value: 'bool'):
        self.wrapped.CompareTorqueRippleAndStatorTorqueReactionDerivedFromStatorTangentialLoads = bool(value) if value else False

    @property
    def use_stator_radius_from_masta_model(self) -> 'bool':
        '''bool: 'UseStatorRadiusFromMASTAModel' is the original name of this property.'''

        return self.wrapped.UseStatorRadiusFromMASTAModel

    @use_stator_radius_from_masta_model.setter
    def use_stator_radius_from_masta_model(self, value: 'bool'):
        self.wrapped.UseStatorRadiusFromMASTAModel = bool(value) if value else False

    @property
    def scale(self) -> 'float':
        '''float: 'Scale' is the original name of this property.'''

        return self.wrapped.Scale

    @scale.setter
    def scale(self, value: 'float'):
        self.wrapped.Scale = float(value) if value else 0.0

    @property
    def apply_to_all_data_types(self) -> 'bool':
        '''bool: 'ApplyToAllDataTypes' is the original name of this property.'''

        return self.wrapped.ApplyToAllDataTypes

    @apply_to_all_data_types.setter
    def apply_to_all_data_types(self, value: 'bool'):
        self.wrapped.ApplyToAllDataTypes = bool(value) if value else False

    @property
    def apply_to_all_speeds_for_selected_data_type(self) -> 'bool':
        '''bool: 'ApplyToAllSpeedsForSelectedDataType' is the original name of this property.'''

        return self.wrapped.ApplyToAllSpeedsForSelectedDataType

    @apply_to_all_speeds_for_selected_data_type.setter
    def apply_to_all_speeds_for_selected_data_type(self, value: 'bool'):
        self.wrapped.ApplyToAllSpeedsForSelectedDataType = bool(value) if value else False

    @property
    def data_type_for_scaling(self) -> 'enum_with_selected_value.EnumWithSelectedValue_HarmonicLoadDataType':
        '''enum_with_selected_value.EnumWithSelectedValue_HarmonicLoadDataType: 'DataTypeForScaling' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_HarmonicLoadDataType.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.DataTypeForScaling, value) if self.wrapped.DataTypeForScaling is not None else None

    @data_type_for_scaling.setter
    def data_type_for_scaling(self, value: 'enum_with_selected_value.EnumWithSelectedValue_HarmonicLoadDataType.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_HarmonicLoadDataType.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.DataTypeForScaling = value

    @property
    def data_type_for_force_distribution_and_temporal_spatial_harmonics_charts(self) -> 'enum_with_selected_value.EnumWithSelectedValue_HarmonicLoadDataType':
        '''enum_with_selected_value.EnumWithSelectedValue_HarmonicLoadDataType: 'DataTypeForForceDistributionAndTemporalSpatialHarmonicsCharts' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_HarmonicLoadDataType.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.DataTypeForForceDistributionAndTemporalSpatialHarmonicsCharts, value) if self.wrapped.DataTypeForForceDistributionAndTemporalSpatialHarmonicsCharts is not None else None

    @data_type_for_force_distribution_and_temporal_spatial_harmonics_charts.setter
    def data_type_for_force_distribution_and_temporal_spatial_harmonics_charts(self, value: 'enum_with_selected_value.EnumWithSelectedValue_HarmonicLoadDataType.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_HarmonicLoadDataType.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.DataTypeForForceDistributionAndTemporalSpatialHarmonicsCharts = value

    @property
    def force_distribution(self) -> 'Image':
        '''Image: 'ForceDistribution' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.ForceDistribution)
        return value

    @property
    def force_distribution_3d(self) -> '_1625.ThreeDVectorChartDefinition':
        '''ThreeDVectorChartDefinition: 'ForceDistribution3D' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1625.ThreeDVectorChartDefinition)(self.wrapped.ForceDistribution3D) if self.wrapped.ForceDistribution3D is not None else None

    @property
    def plot_as_vectors(self) -> 'bool':
        '''bool: 'PlotAsVectors' is the original name of this property.'''

        return self.wrapped.PlotAsVectors

    @plot_as_vectors.setter
    def plot_as_vectors(self, value: 'bool'):
        self.wrapped.PlotAsVectors = bool(value) if value else False

    @property
    def show_all_forces(self) -> 'bool':
        '''bool: 'ShowAllForces' is the original name of this property.'''

        return self.wrapped.ShowAllForces

    @show_all_forces.setter
    def show_all_forces(self, value: 'bool'):
        self.wrapped.ShowAllForces = bool(value) if value else False

    @property
    def invert_axis(self) -> 'bool':
        '''bool: 'InvertAxis' is the original name of this property.'''

        return self.wrapped.InvertAxis

    @invert_axis.setter
    def invert_axis(self, value: 'bool'):
        self.wrapped.InvertAxis = bool(value) if value else False

    @property
    def excitations(self) -> 'List[_1312.FourierSeries]':
        '''List[FourierSeries]: 'Excitations' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Excitations, constructor.new(_1312.FourierSeries))
        return value
