'''_1280.py

LoadedBolt
'''


from typing import List

from mastapy.bolts import (
    _1263, _1279, _1285, _1275
)
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._math.vector_3d import Vector3D
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_LOADED_BOLT = python_net_import('SMT.MastaAPI.Bolts', 'LoadedBolt')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedBolt',)


class LoadedBolt(_0.APIBase):
    '''LoadedBolt

    This is a mastapy class.
    '''

    TYPE = _LOADED_BOLT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedBolt.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def axial_load_type(self) -> '_1263.AxialLoadType':
        '''AxialLoadType: 'AxialLoadType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.AxialLoadType)
        return constructor.new(_1263.AxialLoadType)(value) if value is not None else None

    @axial_load_type.setter
    def axial_load_type(self, value: '_1263.AxialLoadType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.AxialLoadType = value

    @property
    def assembly_preload(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'AssemblyPreload' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.AssemblyPreload) if self.wrapped.AssemblyPreload is not None else None

    @assembly_preload.setter
    def assembly_preload(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.AssemblyPreload = value

    @property
    def maximum_transverse_load(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MaximumTransverseLoad' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MaximumTransverseLoad) if self.wrapped.MaximumTransverseLoad is not None else None

    @maximum_transverse_load.setter
    def maximum_transverse_load(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MaximumTransverseLoad = value

    @property
    def maximum_torque_about_bolt_axis(self) -> 'float':
        '''float: 'MaximumTorqueAboutBoltAxis' is the original name of this property.'''

        return self.wrapped.MaximumTorqueAboutBoltAxis

    @maximum_torque_about_bolt_axis.setter
    def maximum_torque_about_bolt_axis(self, value: 'float'):
        self.wrapped.MaximumTorqueAboutBoltAxis = float(value) if value else 0.0

    @property
    def maximum_torsional_moment(self) -> 'float':
        '''float: 'MaximumTorsionalMoment' is the original name of this property.'''

        return self.wrapped.MaximumTorsionalMoment

    @maximum_torsional_moment.setter
    def maximum_torsional_moment(self, value: 'float'):
        self.wrapped.MaximumTorsionalMoment = float(value) if value else 0.0

    @property
    def maximum_pressure_to_be_sealed(self) -> 'float':
        '''float: 'MaximumPressureToBeSealed' is the original name of this property.'''

        return self.wrapped.MaximumPressureToBeSealed

    @maximum_pressure_to_be_sealed.setter
    def maximum_pressure_to_be_sealed(self, value: 'float'):
        self.wrapped.MaximumPressureToBeSealed = float(value) if value else 0.0

    @property
    def edge_distance_of_opening_point_u(self) -> 'float':
        '''float: 'EdgeDistanceOfOpeningPointU' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EdgeDistanceOfOpeningPointU

    @property
    def distance_of_edge_bearing_point_v_from_centre(self) -> 'float':
        '''float: 'DistanceOfEdgeBearingPointVFromCentre' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DistanceOfEdgeBearingPointVFromCentre

    @property
    def bending_moment(self) -> 'float':
        '''float: 'BendingMoment' is the original name of this property.'''

        return self.wrapped.BendingMoment

    @bending_moment.setter
    def bending_moment(self, value: 'float'):
        self.wrapped.BendingMoment = float(value) if value else 0.0

    @property
    def bending_moment_at_bolting_point(self) -> 'float':
        '''float: 'BendingMomentAtBoltingPoint' is the original name of this property.'''

        return self.wrapped.BendingMomentAtBoltingPoint

    @bending_moment_at_bolting_point.setter
    def bending_moment_at_bolting_point(self, value: 'float'):
        self.wrapped.BendingMomentAtBoltingPoint = float(value) if value else 0.0

    @property
    def maximum_axial_load(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MaximumAxialLoad' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MaximumAxialLoad) if self.wrapped.MaximumAxialLoad is not None else None

    @maximum_axial_load.setter
    def maximum_axial_load(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MaximumAxialLoad = value

    @property
    def minimum_axial_load(self) -> 'float':
        '''float: 'MinimumAxialLoad' is the original name of this property.'''

        return self.wrapped.MinimumAxialLoad

    @minimum_axial_load.setter
    def minimum_axial_load(self, value: 'float'):
        self.wrapped.MinimumAxialLoad = float(value) if value else 0.0

    @property
    def change_in_temperature_of_bolt(self) -> 'float':
        '''float: 'ChangeInTemperatureOfBolt' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ChangeInTemperatureOfBolt

    @property
    def change_in_temperature_of_clamped_parts(self) -> 'float':
        '''float: 'ChangeInTemperatureOfClampedParts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ChangeInTemperatureOfClampedParts

    @property
    def operating_temperature_of_bolt(self) -> 'float':
        '''float: 'OperatingTemperatureOfBolt' is the original name of this property.'''

        return self.wrapped.OperatingTemperatureOfBolt

    @operating_temperature_of_bolt.setter
    def operating_temperature_of_bolt(self, value: 'float'):
        self.wrapped.OperatingTemperatureOfBolt = float(value) if value else 0.0

    @property
    def assembly_temperature(self) -> 'float':
        '''float: 'AssemblyTemperature' is the original name of this property.'''

        return self.wrapped.AssemblyTemperature

    @assembly_temperature.setter
    def assembly_temperature(self, value: 'float'):
        self.wrapped.AssemblyTemperature = float(value) if value else 0.0

    @property
    def operating_temperature_of_clamped_parts(self) -> 'float':
        '''float: 'OperatingTemperatureOfClampedParts' is the original name of this property.'''

        return self.wrapped.OperatingTemperatureOfClampedParts

    @operating_temperature_of_clamped_parts.setter
    def operating_temperature_of_clamped_parts(self, value: 'float'):
        self.wrapped.OperatingTemperatureOfClampedParts = float(value) if value else 0.0

    @property
    def preload(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Preload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Preload) if self.wrapped.Preload is not None else None

    @property
    def preload_in_assembled_state(self) -> 'float':
        '''float: 'PreloadInAssembledState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PreloadInAssembledState

    @property
    def tabular_tightening_torque(self) -> 'float':
        '''float: 'TabularTighteningTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TabularTighteningTorque

    @property
    def number_of_alternating_cycles_during_continuous_loading(self) -> 'float':
        '''float: 'NumberOfAlternatingCyclesDuringContinuousLoading' is the original name of this property.'''

        return self.wrapped.NumberOfAlternatingCyclesDuringContinuousLoading

    @number_of_alternating_cycles_during_continuous_loading.setter
    def number_of_alternating_cycles_during_continuous_loading(self, value: 'float'):
        self.wrapped.NumberOfAlternatingCyclesDuringContinuousLoading = float(value) if value else 0.0

    @property
    def number_of_alternating_cycles_during_loading_within_fatigue_range(self) -> 'float':
        '''float: 'NumberOfAlternatingCyclesDuringLoadingWithinFatigueRange' is the original name of this property.'''

        return self.wrapped.NumberOfAlternatingCyclesDuringLoadingWithinFatigueRange

    @number_of_alternating_cycles_during_loading_within_fatigue_range.setter
    def number_of_alternating_cycles_during_loading_within_fatigue_range(self, value: 'float'):
        self.wrapped.NumberOfAlternatingCyclesDuringLoadingWithinFatigueRange = float(value) if value else 0.0

    @property
    def number_of_bearing_areas(self) -> 'int':
        '''int: 'NumberOfBearingAreas' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfBearingAreas

    @property
    def plastic_deformation_due_to_embedding(self) -> 'float':
        '''float: 'PlasticDeformationDueToEmbedding' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PlasticDeformationDueToEmbedding

    @property
    def fatigue_safety_factor_in_working_state(self) -> 'float':
        '''float: 'FatigueSafetyFactorInWorkingState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FatigueSafetyFactorInWorkingState

    @property
    def fatigue_safety_factor_in_assembled_state(self) -> 'float':
        '''float: 'FatigueSafetyFactorInAssembledState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FatigueSafetyFactorInAssembledState

    @property
    def surface_pressure_safety_factor(self) -> 'float':
        '''float: 'SurfacePressureSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfacePressureSafetyFactor

    @property
    def surface_pressure_safety_factor_in_working_state(self) -> 'float':
        '''float: 'SurfacePressureSafetyFactorInWorkingState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfacePressureSafetyFactorInWorkingState

    @property
    def surface_pressure_safety_factor_in_assembled_state(self) -> 'float':
        '''float: 'SurfacePressureSafetyFactorInAssembledState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfacePressureSafetyFactorInAssembledState

    @property
    def surface_pressure_safety_factor_on_nut_side(self) -> 'float':
        '''float: 'SurfacePressureSafetyFactorOnNutSide' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfacePressureSafetyFactorOnNutSide

    @property
    def surface_pressure_safety_factor_on_head_side(self) -> 'float':
        '''float: 'SurfacePressureSafetyFactorOnHeadSide' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfacePressureSafetyFactorOnHeadSide

    @property
    def surface_pressure_safety_factor_on_nut_side_in_working_state(self) -> 'float':
        '''float: 'SurfacePressureSafetyFactorOnNutSideInWorkingState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfacePressureSafetyFactorOnNutSideInWorkingState

    @property
    def surface_pressure_safety_factor_on_head_side_in_working_state(self) -> 'float':
        '''float: 'SurfacePressureSafetyFactorOnHeadSideInWorkingState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfacePressureSafetyFactorOnHeadSideInWorkingState

    @property
    def limiting_surface_pressure_on_head_side(self) -> 'float':
        '''float: 'LimitingSurfacePressureOnHeadSide' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LimitingSurfacePressureOnHeadSide

    @property
    def limiting_surface_pressure_on_nut_side(self) -> 'float':
        '''float: 'LimitingSurfacePressureOnNutSide' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LimitingSurfacePressureOnNutSide

    @property
    def slipping_safety_factor(self) -> 'float':
        '''float: 'SlippingSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SlippingSafetyFactor

    @property
    def slipping_safety_factor_in_the_assembled_state(self) -> 'float':
        '''float: 'SlippingSafetyFactorInTheAssembledState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SlippingSafetyFactorInTheAssembledState

    @property
    def slipping_safety_factor_in_the_assembled_state_minimum_assembly_preload(self) -> 'float':
        '''float: 'SlippingSafetyFactorInTheAssembledStateMinimumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SlippingSafetyFactorInTheAssembledStateMinimumAssemblyPreload

    @property
    def slipping_safety_factor_in_the_assembled_state_maximum_assembly_preload(self) -> 'float':
        '''float: 'SlippingSafetyFactorInTheAssembledStateMaximumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SlippingSafetyFactorInTheAssembledStateMaximumAssemblyPreload

    @property
    def shearing_safety_factor(self) -> 'float':
        '''float: 'ShearingSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShearingSafetyFactor

    @property
    def minimum_required_clamping_force(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MinimumRequiredClampingForce' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MinimumRequiredClampingForce) if self.wrapped.MinimumRequiredClampingForce is not None else None

    @minimum_required_clamping_force.setter
    def minimum_required_clamping_force(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MinimumRequiredClampingForce = value

    @property
    def minimum_clamp_load_at_the_opening_limit(self) -> 'float':
        '''float: 'MinimumClampLoadAtTheOpeningLimit' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumClampLoadAtTheOpeningLimit

    @property
    def load_factor(self) -> 'float':
        '''float: 'LoadFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadFactor

    @property
    def theoretical_load_factor(self) -> 'float':
        '''float: 'TheoreticalLoadFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TheoreticalLoadFactor

    @property
    def relieving_load_of_plates(self) -> 'float':
        '''float: 'RelievingLoadOfPlates' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelievingLoadOfPlates

    @property
    def joint_type(self) -> '_1279.JointTypes':
        '''JointTypes: 'JointType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.JointType)
        return constructor.new(_1279.JointTypes)(value) if value is not None else None

    @joint_type.setter
    def joint_type(self, value: '_1279.JointTypes'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.JointType = value

    @property
    def length_between_basic_solid_and_load_introduction_point_k(self) -> 'float':
        '''float: 'LengthBetweenBasicSolidAndLoadIntroductionPointK' is the original name of this property.'''

        return self.wrapped.LengthBetweenBasicSolidAndLoadIntroductionPointK

    @length_between_basic_solid_and_load_introduction_point_k.setter
    def length_between_basic_solid_and_load_introduction_point_k(self, value: 'float'):
        self.wrapped.LengthBetweenBasicSolidAndLoadIntroductionPointK = float(value) if value else 0.0

    @property
    def distance_of_line_of_action_of_axial_load_from_centre(self) -> 'float':
        '''float: 'DistanceOfLineOfActionOfAxialLoadFromCentre' is the original name of this property.'''

        return self.wrapped.DistanceOfLineOfActionOfAxialLoadFromCentre

    @distance_of_line_of_action_of_axial_load_from_centre.setter
    def distance_of_line_of_action_of_axial_load_from_centre(self, value: 'float'):
        self.wrapped.DistanceOfLineOfActionOfAxialLoadFromCentre = float(value) if value else 0.0

    @property
    def distance_between_edge_of_preloading_area_and_force_introduction_point(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DistanceBetweenEdgeOfPreloadingAreaAndForceIntroductionPoint' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DistanceBetweenEdgeOfPreloadingAreaAndForceIntroductionPoint) if self.wrapped.DistanceBetweenEdgeOfPreloadingAreaAndForceIntroductionPoint is not None else None

    @distance_between_edge_of_preloading_area_and_force_introduction_point.setter
    def distance_between_edge_of_preloading_area_and_force_introduction_point(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.DistanceBetweenEdgeOfPreloadingAreaAndForceIntroductionPoint = value

    @property
    def maximum_relieving_load_of_plates(self) -> 'float':
        '''float: 'MaximumRelievingLoadOfPlates' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumRelievingLoadOfPlates

    @property
    def load_factor_for_concentric_clamping(self) -> 'float':
        '''float: 'LoadFactorForConcentricClamping' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadFactorForConcentricClamping

    @property
    def load_factor_for_concentric_clamping_in_operating_state(self) -> 'float':
        '''float: 'LoadFactorForConcentricClampingInOperatingState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadFactorForConcentricClampingInOperatingState

    @property
    def load_factor_for_eccentric_clamping_and_concentric_load_introduction(self) -> 'float':
        '''float: 'LoadFactorForEccentricClampingAndConcentricLoadIntroduction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadFactorForEccentricClampingAndConcentricLoadIntroduction

    @property
    def load_factor_for_eccentric_clamping(self) -> 'float':
        '''float: 'LoadFactorForEccentricClamping' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadFactorForEccentricClamping

    @property
    def load_factor_phi_stare_k(self) -> 'float':
        '''float: 'LoadFactorPhiStareK' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadFactorPhiStareK

    @property
    def load_factor_bending(self) -> 'float':
        '''float: 'LoadFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadFactorBending

    @property
    def loss_of_preload_due_to_embedding(self) -> 'float':
        '''float: 'LossOfPreloadDueToEmbedding' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LossOfPreloadDueToEmbedding

    @property
    def load_introduction_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'LoadIntroductionFactor' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.LoadIntroductionFactor) if self.wrapped.LoadIntroductionFactor is not None else None

    @load_introduction_factor.setter
    def load_introduction_factor(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.LoadIntroductionFactor = value

    @property
    def change_in_preload_due_to_thermal_expansion(self) -> 'float':
        '''float: 'ChangeInPreloadDueToThermalExpansion' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ChangeInPreloadDueToThermalExpansion

    @property
    def minimum_assembly_preload(self) -> 'float':
        '''float: 'MinimumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumAssemblyPreload

    @property
    def minimum_assembly_preload_during_assembly(self) -> 'float':
        '''float: 'MinimumAssemblyPreloadDuringAssembly' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumAssemblyPreloadDuringAssembly

    @property
    def maximum_assembly_preload(self) -> 'float':
        '''float: 'MaximumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumAssemblyPreload

    @property
    def maximum_assembly_preload_during_assembly(self) -> 'float':
        '''float: 'MaximumAssemblyPreloadDuringAssembly' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumAssemblyPreloadDuringAssembly

    @property
    def tightening_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'TighteningFactor' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.TighteningFactor) if self.wrapped.TighteningFactor is not None else None

    @tightening_factor.setter
    def tightening_factor(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.TighteningFactor = value

    @property
    def permitted_assembly_reduced_stress(self) -> 'float':
        '''float: 'PermittedAssemblyReducedStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermittedAssemblyReducedStress

    @property
    def permissible_assembly_preload(self) -> 'float':
        '''float: 'PermissibleAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleAssemblyPreload

    @property
    def permissible_assembly_preload_assembled_state(self) -> 'float':
        '''float: 'PermissibleAssemblyPreloadAssembledState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleAssemblyPreloadAssembledState

    @property
    def total_bolt_load(self) -> 'float':
        '''float: 'TotalBoltLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalBoltLoad

    @property
    def maximum_tensile_stress(self) -> 'float':
        '''float: 'MaximumTensileStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumTensileStress

    @property
    def maximum_torsional_stress(self) -> 'float':
        '''float: 'MaximumTorsionalStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumTorsionalStress

    @property
    def maximum_torsional_stress_due_to_fq(self) -> 'float':
        '''float: 'MaximumTorsionalStressDueToFQ' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumTorsionalStressDueToFQ

    @property
    def proportion_of_tightening_torque_in_thread(self) -> 'float':
        '''float: 'ProportionOfTighteningTorqueInThread' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProportionOfTighteningTorqueInThread

    @property
    def polar_moment_of_resistance(self) -> 'float':
        '''float: 'PolarMomentOfResistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PolarMomentOfResistance

    @property
    def comparative_stress_in_working_state(self) -> 'float':
        '''float: 'ComparativeStressInWorkingState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ComparativeStressInWorkingState

    @property
    def yield_point_safety_factor_in_working_state(self) -> 'float':
        '''float: 'YieldPointSafetyFactorInWorkingState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.YieldPointSafetyFactorInWorkingState

    @property
    def yield_point_safety_factor_in_assembled_state(self) -> 'float':
        '''float: 'YieldPointSafetyFactorInAssembledState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.YieldPointSafetyFactorInAssembledState

    @property
    def surface_pressure_safety_factor_maximum_required_assembly_preload(self) -> 'float':
        '''float: 'SurfacePressureSafetyFactorMaximumRequiredAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfacePressureSafetyFactorMaximumRequiredAssemblyPreload

    @property
    def surface_pressure_safety_factor_in_the_assembled_state_minimum_required_assembly_preload(self) -> 'float':
        '''float: 'SurfacePressureSafetyFactorInTheAssembledStateMinimumRequiredAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfacePressureSafetyFactorInTheAssembledStateMinimumRequiredAssemblyPreload

    @property
    def surface_pressure_safety_factor_minimum_required_assembly_preload(self) -> 'float':
        '''float: 'SurfacePressureSafetyFactorMinimumRequiredAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfacePressureSafetyFactorMinimumRequiredAssemblyPreload

    @property
    def maximum_surface_pressure_in_working_state_maximum_assembly_preload(self) -> 'float':
        '''float: 'MaximumSurfacePressureInWorkingStateMaximumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumSurfacePressureInWorkingStateMaximumAssemblyPreload

    @property
    def maximum_surface_pressure_in_assembled_state_maximum_assembly_preload(self) -> 'float':
        '''float: 'MaximumSurfacePressureInAssembledStateMaximumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumSurfacePressureInAssembledStateMaximumAssemblyPreload

    @property
    def maximum_surface_pressure_in_working_state_minimum_assembly_preload(self) -> 'float':
        '''float: 'MaximumSurfacePressureInWorkingStateMinimumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumSurfacePressureInWorkingStateMinimumAssemblyPreload

    @property
    def maximum_preload_in_assembled_state_maximum_assembly_preload(self) -> 'float':
        '''float: 'MaximumPreloadInAssembledStateMaximumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPreloadInAssembledStateMaximumAssemblyPreload

    @property
    def maximum_preload_maximum_assembly_preload(self) -> 'float':
        '''float: 'MaximumPreloadMaximumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPreloadMaximumAssemblyPreload

    @property
    def maximum_preload_minimum_assembly_preload(self) -> 'float':
        '''float: 'MaximumPreloadMinimumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPreloadMinimumAssemblyPreload

    @property
    def slipping_safety_factor_maximum_required_assembly_preload(self) -> 'float':
        '''float: 'SlippingSafetyFactorMaximumRequiredAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SlippingSafetyFactorMaximumRequiredAssemblyPreload

    @property
    def slipping_safety_factor_minimum_required_assembly_preload(self) -> 'float':
        '''float: 'SlippingSafetyFactorMinimumRequiredAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SlippingSafetyFactorMinimumRequiredAssemblyPreload

    @property
    def minimum_residual_clamp_load_maximum_assembly_preload(self) -> 'float':
        '''float: 'MinimumResidualClampLoadMaximumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumResidualClampLoadMaximumAssemblyPreload

    @property
    def minimum_residual_clamp_load_minimum_assembly_preload(self) -> 'float':
        '''float: 'MinimumResidualClampLoadMinimumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumResidualClampLoadMinimumAssemblyPreload

    @property
    def fatigue_safety_factor_maximum_required_assembly_preload(self) -> 'float':
        '''float: 'FatigueSafetyFactorMaximumRequiredAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FatigueSafetyFactorMaximumRequiredAssemblyPreload

    @property
    def fatigue_safety_factor_minimum_required_assembly_preload(self) -> 'float':
        '''float: 'FatigueSafetyFactorMinimumRequiredAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FatigueSafetyFactorMinimumRequiredAssemblyPreload

    @property
    def fatigue_safety_factor_in_the_assembled_state_maximum_required_assembly_preload(self) -> 'float':
        '''float: 'FatigueSafetyFactorInTheAssembledStateMaximumRequiredAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FatigueSafetyFactorInTheAssembledStateMaximumRequiredAssemblyPreload

    @property
    def fatigue_safety_factor_in_the_assembled_state_minimum_required_assembly_preload(self) -> 'float':
        '''float: 'FatigueSafetyFactorInTheAssembledStateMinimumRequiredAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FatigueSafetyFactorInTheAssembledStateMinimumRequiredAssemblyPreload

    @property
    def stress_amplitude_of_fatigue_strength_sg_maximum_assembly_preload(self) -> 'float':
        '''float: 'StressAmplitudeOfFatigueStrengthSGMaximumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressAmplitudeOfFatigueStrengthSGMaximumAssemblyPreload

    @property
    def stress_amplitude_of_fatigue_strength_sg_minimum_assembly_preload(self) -> 'float':
        '''float: 'StressAmplitudeOfFatigueStrengthSGMinimumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressAmplitudeOfFatigueStrengthSGMinimumAssemblyPreload

    @property
    def stress_amplitude_of_endurance_limit_sg_maximum_assembly_preload(self) -> 'float':
        '''float: 'StressAmplitudeOfEnduranceLimitSGMaximumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressAmplitudeOfEnduranceLimitSGMaximumAssemblyPreload

    @property
    def stress_amplitude_of_endurance_limit_sg_minimum_assembly_preload(self) -> 'float':
        '''float: 'StressAmplitudeOfEnduranceLimitSGMinimumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressAmplitudeOfEnduranceLimitSGMinimumAssemblyPreload

    @property
    def average_bolt_load_maximum_assembly_preload(self) -> 'float':
        '''float: 'AverageBoltLoadMaximumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageBoltLoadMaximumAssemblyPreload

    @property
    def average_bolt_load_minimum_assembly_preload(self) -> 'float':
        '''float: 'AverageBoltLoadMinimumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageBoltLoadMinimumAssemblyPreload

    @property
    def yield_point_safety_factor_in_working_state_maximum_required_assembly_preload(self) -> 'float':
        '''float: 'YieldPointSafetyFactorInWorkingStateMaximumRequiredAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.YieldPointSafetyFactorInWorkingStateMaximumRequiredAssemblyPreload

    @property
    def yield_point_safety_factor_in_assembled_state_maximum_required_assembly_preload(self) -> 'float':
        '''float: 'YieldPointSafetyFactorInAssembledStateMaximumRequiredAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.YieldPointSafetyFactorInAssembledStateMaximumRequiredAssemblyPreload

    @property
    def yield_point_safety_factor_in_working_state_minimum_required_assembly_preload(self) -> 'float':
        '''float: 'YieldPointSafetyFactorInWorkingStateMinimumRequiredAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.YieldPointSafetyFactorInWorkingStateMinimumRequiredAssemblyPreload

    @property
    def comparative_stress_in_working_state_minimum_assembly_preload(self) -> 'float':
        '''float: 'ComparativeStressInWorkingStateMinimumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ComparativeStressInWorkingStateMinimumAssemblyPreload

    @property
    def comparative_stress_in_working_state_maximum_assembly_preload(self) -> 'float':
        '''float: 'ComparativeStressInWorkingStateMaximumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ComparativeStressInWorkingStateMaximumAssemblyPreload

    @property
    def total_bolt_load_maximum_assembly_preload(self) -> 'float':
        '''float: 'TotalBoltLoadMaximumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalBoltLoadMaximumAssemblyPreload

    @property
    def total_bolt_load_minimum_assembly_preload(self) -> 'float':
        '''float: 'TotalBoltLoadMinimumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalBoltLoadMinimumAssemblyPreload

    @property
    def maximum_tensile_stress_in_working_state_maximum_assembly_preload(self) -> 'float':
        '''float: 'MaximumTensileStressInWorkingStateMaximumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumTensileStressInWorkingStateMaximumAssemblyPreload

    @property
    def maximum_tensile_stress_in_working_state_minimum_assembly_preload(self) -> 'float':
        '''float: 'MaximumTensileStressInWorkingStateMinimumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumTensileStressInWorkingStateMinimumAssemblyPreload

    @property
    def alternating_stress(self) -> 'float':
        '''float: 'AlternatingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AlternatingStress

    @property
    def alternating_stress_eccentric(self) -> 'float':
        '''float: 'AlternatingStressEccentric' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AlternatingStressEccentric

    @property
    def minimum_residual_clamp_load(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MinimumResidualClampLoad' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MinimumResidualClampLoad) if self.wrapped.MinimumResidualClampLoad is not None else None

    @minimum_residual_clamp_load.setter
    def minimum_residual_clamp_load(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MinimumResidualClampLoad = value

    @property
    def minimum_residual_clamp_load_in_assembled_state(self) -> 'float':
        '''float: 'MinimumResidualClampLoadInAssembledState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumResidualClampLoadInAssembledState

    @property
    def minimum_clamp_load_for_transmitting_transverse_load(self) -> 'float':
        '''float: 'MinimumClampLoadForTransmittingTransverseLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumClampLoadForTransmittingTransverseLoad

    @property
    def tightening_torque(self) -> 'float':
        '''float: 'TighteningTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TighteningTorque

    @property
    def tightening_torque_minimum_assembly_preload(self) -> 'float':
        '''float: 'TighteningTorqueMinimumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TighteningTorqueMinimumAssemblyPreload

    @property
    def tightening_torque_maximum_assembly_preload(self) -> 'float':
        '''float: 'TighteningTorqueMaximumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TighteningTorqueMaximumAssemblyPreload

    @property
    def bending_angle(self) -> 'float':
        '''float: 'BendingAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BendingAngle

    @property
    def resulting_moment_in_clamping_area(self) -> 'float':
        '''float: 'ResultingMomentInClampingArea' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ResultingMomentInClampingArea

    @property
    def preload_at_room_temperature(self) -> 'float':
        '''float: 'PreloadAtRoomTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PreloadAtRoomTemperature

    @property
    def elastic_resilience_of_bolt_at_room_temperature(self) -> 'float':
        '''float: 'ElasticResilienceOfBoltAtRoomTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ElasticResilienceOfBoltAtRoomTemperature

    @property
    def elastic_resilience_of_plates_at_room_temperature(self) -> 'float':
        '''float: 'ElasticResilienceOfPlatesAtRoomTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ElasticResilienceOfPlatesAtRoomTemperature

    @property
    def comparative_stress_in_assembled_state(self) -> 'float':
        '''float: 'ComparativeStressInAssembledState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ComparativeStressInAssembledState

    @property
    def comparative_stress_in_assembled_state_maximum_assembly_preload(self) -> 'float':
        '''float: 'ComparativeStressInAssembledStateMaximumAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ComparativeStressInAssembledStateMaximumAssemblyPreload

    @property
    def tensile_stress_due_to_assembly_preload(self) -> 'float':
        '''float: 'TensileStressDueToAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TensileStressDueToAssemblyPreload

    @property
    def torsional_stress_in_assembled_state(self) -> 'float':
        '''float: 'TorsionalStressInAssembledState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TorsionalStressInAssembledState

    @property
    def stress_amplitude_of_endurance_limit_sg(self) -> 'float':
        '''float: 'StressAmplitudeOfEnduranceLimitSG' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressAmplitudeOfEnduranceLimitSG

    @property
    def stress_amplitude_of_endurance_limit_sv(self) -> 'float':
        '''float: 'StressAmplitudeOfEnduranceLimitSV' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressAmplitudeOfEnduranceLimitSV

    @property
    def stress_amplitude_of_fatigue_strength_sg(self) -> 'float':
        '''float: 'StressAmplitudeOfFatigueStrengthSG' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressAmplitudeOfFatigueStrengthSG

    @property
    def stress_amplitude_of_fatigue_strength_sv(self) -> 'float':
        '''float: 'StressAmplitudeOfFatigueStrengthSV' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressAmplitudeOfFatigueStrengthSV

    @property
    def load_at_minimum_yield_point(self) -> 'float':
        '''float: 'LoadAtMinimumYieldPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadAtMinimumYieldPoint

    @property
    def average_bolt_load(self) -> 'float':
        '''float: 'AverageBoltLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageBoltLoad

    @property
    def stress_in_bending_tension_of_bolt_thread(self) -> 'float':
        '''float: 'StressInBendingTensionOfBoltThread' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressInBendingTensionOfBoltThread

    @property
    def stripping_force(self) -> 'float':
        '''float: 'StrippingForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StrippingForce

    @property
    def breaking_force(self) -> 'float':
        '''float: 'BreakingForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BreakingForce

    @property
    def minimum_length_of_engagement(self) -> 'float':
        '''float: 'MinimumLengthOfEngagement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumLengthOfEngagement

    @property
    def minimum_effective_length_of_engagement(self) -> 'float':
        '''float: 'MinimumEffectiveLengthOfEngagement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumEffectiveLengthOfEngagement

    @property
    def present_length_of_engagement(self) -> 'float':
        '''float: 'PresentLengthOfEngagement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PresentLengthOfEngagement

    @property
    def present_effective_length_of_engagement(self) -> 'float':
        '''float: 'PresentEffectiveLengthOfEngagement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PresentEffectiveLengthOfEngagement

    @property
    def shearing_cross_section_of_nut_thread(self) -> 'float':
        '''float: 'ShearingCrossSectionOfNutThread' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShearingCrossSectionOfNutThread

    @property
    def shearing_cross_section_of_bolt_thread(self) -> 'float':
        '''float: 'ShearingCrossSectionOfBoltThread' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShearingCrossSectionOfBoltThread

    @property
    def correction_factor_c1(self) -> 'float':
        '''float: 'CorrectionFactorC1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CorrectionFactorC1

    @property
    def correction_factor_c3(self) -> 'float':
        '''float: 'CorrectionFactorC3' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CorrectionFactorC3

    @property
    def strength_ratio(self) -> 'float':
        '''float: 'StrengthRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StrengthRatio

    @property
    def residual_transverse_load(self) -> 'float':
        '''float: 'ResidualTransverseLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ResidualTransverseLoad

    @property
    def limiting_slip_force(self) -> 'float':
        '''float: 'LimitingSlipForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LimitingSlipForce

    @property
    def permissible_shearing_force_of_bolt(self) -> 'float':
        '''float: 'PermissibleShearingForceOfBolt' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleShearingForceOfBolt

    @property
    def elastic_resilience_of_bolt(self) -> 'float':
        '''float: 'ElasticResilienceOfBolt' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ElasticResilienceOfBolt

    @property
    def elastic_resilience_of_bolt_in_operating_state(self) -> 'float':
        '''float: 'ElasticResilienceOfBoltInOperatingState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ElasticResilienceOfBoltInOperatingState

    @property
    def tabular_assembly_preload(self) -> 'float':
        '''float: 'TabularAssemblyPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TabularAssemblyPreload

    @property
    def effective_diameter_of_friction_moment(self) -> 'float':
        '''float: 'EffectiveDiameterOfFrictionMoment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EffectiveDiameterOfFrictionMoment

    @property
    def total_bending_moment(self) -> 'float':
        '''float: 'TotalBendingMoment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalBendingMoment

    @property
    def total_bending_moment_in_bolt(self) -> 'float':
        '''float: 'TotalBendingMomentInBolt' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalBendingMomentInBolt

    @property
    def total_bending_moment_in_plates(self) -> 'float':
        '''float: 'TotalBendingMomentInPlates' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalBendingMomentInPlates

    @property
    def axial_load_at_opening_limit_eccentric_loading(self) -> 'float':
        '''float: 'AxialLoadAtOpeningLimitEccentricLoading' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AxialLoadAtOpeningLimitEccentricLoading

    @property
    def axial_load_at_opening_limit_eccentric_loading_from_5329(self) -> 'float':
        '''float: 'AxialLoadAtOpeningLimitEccentricLoadingFrom5329' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AxialLoadAtOpeningLimitEccentricLoadingFrom5329

    @property
    def axial_load_at_opening_limit_concentric_loading(self) -> 'float':
        '''float: 'AxialLoadAtOpeningLimitConcentricLoading' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AxialLoadAtOpeningLimitConcentricLoading

    @property
    def preload_at_opening_limit(self) -> 'float':
        '''float: 'PreloadAtOpeningLimit' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PreloadAtOpeningLimit

    @property
    def clamp_load_at_opening_limit(self) -> 'float':
        '''float: 'ClampLoadAtOpeningLimit' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ClampLoadAtOpeningLimit

    @property
    def minimum_clamp_load_for_ensuring_a_sealing_function(self) -> 'float':
        '''float: 'MinimumClampLoadForEnsuringASealingFunction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumClampLoadForEnsuringASealingFunction

    @property
    def additional_bolt_load_after_opening(self) -> 'float':
        '''float: 'AdditionalBoltLoadAfterOpening' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AdditionalBoltLoadAfterOpening

    @property
    def additional_bending_moment(self) -> 'float':
        '''float: 'AdditionalBendingMoment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AdditionalBendingMoment

    @property
    def additional_bending_moment_in_bolt(self) -> 'float':
        '''float: 'AdditionalBendingMomentInBolt' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AdditionalBendingMomentInBolt

    @property
    def maximum_surface_pressure(self) -> 'float':
        '''float: 'MaximumSurfacePressure' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumSurfacePressure

    @property
    def maximum_surface_pressure_in_assembled_state(self) -> 'float':
        '''float: 'MaximumSurfacePressureInAssembledState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumSurfacePressureInAssembledState

    @property
    def maximum_head_surface_pressure_in_assembled_state(self) -> 'float':
        '''float: 'MaximumHeadSurfacePressureInAssembledState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumHeadSurfacePressureInAssembledState

    @property
    def maximum_nut_surface_pressure_in_assembled_state(self) -> 'float':
        '''float: 'MaximumNutSurfacePressureInAssembledState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumNutSurfacePressureInAssembledState

    @property
    def maximum_surface_pressure_in_working_state(self) -> 'float':
        '''float: 'MaximumSurfacePressureInWorkingState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumSurfacePressureInWorkingState

    @property
    def maximum_head_surface_pressure_in_working_state(self) -> 'float':
        '''float: 'MaximumHeadSurfacePressureInWorkingState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumHeadSurfacePressureInWorkingState

    @property
    def maximum_nut_surface_pressure_in_working_state(self) -> 'float':
        '''float: 'MaximumNutSurfacePressureInWorkingState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumNutSurfacePressureInWorkingState

    @property
    def clamping_load(self) -> 'float':
        '''float: 'ClampingLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ClampingLoad

    @property
    def additional_axial_bolt_load(self) -> 'float':
        '''float: 'AdditionalAxialBoltLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AdditionalAxialBoltLoad

    @property
    def additional_axial_bolt_load_in_assembled_state(self) -> 'float':
        '''float: 'AdditionalAxialBoltLoadInAssembledState' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AdditionalAxialBoltLoadInAssembledState

    @property
    def maximum_additional_axial_load(self) -> 'float':
        '''float: 'MaximumAdditionalAxialLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumAdditionalAxialLoad

    @property
    def minimum_additional_axial_load(self) -> 'float':
        '''float: 'MinimumAdditionalAxialLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumAdditionalAxialLoad

    @property
    def maximum_stress_in_bending_tension_of_bolt_thread(self) -> 'float':
        '''float: 'MaximumStressInBendingTensionOfBoltThread' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumStressInBendingTensionOfBoltThread

    @property
    def minimum_stress_in_bending_tension_of_bolt_thread(self) -> 'float':
        '''float: 'MinimumStressInBendingTensionOfBoltThread' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumStressInBendingTensionOfBoltThread

    @property
    def maximum_preload(self) -> 'float':
        '''float: 'MaximumPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPreload

    @property
    def minimum_preload(self) -> 'float':
        '''float: 'MinimumPreload' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumPreload

    @property
    def axial_load_at_which_opening_occurs_during_eccentric_loading(self) -> 'float':
        '''float: 'AxialLoadAtWhichOpeningOccursDuringEccentricLoading' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AxialLoadAtWhichOpeningOccursDuringEccentricLoading

    @property
    def parameter_of_circle_equation_mk(self) -> 'float':
        '''float: 'ParameterOfCircleEquationMK' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ParameterOfCircleEquationMK

    @property
    def parameter_of_circle_equation_nk(self) -> 'float':
        '''float: 'ParameterOfCircleEquationNK' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ParameterOfCircleEquationNK

    @property
    def minimum_nominal_diameter(self) -> 'float':
        '''float: 'MinimumNominalDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumNominalDiameter

    @property
    def number_of_steps_for_f_mmin_table_a7(self) -> 'int':
        '''int: 'NumberOfStepsForFMminTableA7' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfStepsForFMminTableA7

    @property
    def number_of_steps_for_f_mmax_table_a7(self) -> 'int':
        '''int: 'NumberOfStepsForFMmaxTableA7' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfStepsForFMmaxTableA7

    @property
    def joint_is_to_be_designed_with_f_qmax(self) -> 'bool':
        '''bool: 'JointIsToBeDesignedWithFQmax' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.JointIsToBeDesignedWithFQmax

    @property
    def does_tightening_technique_exceed_yield_point(self) -> 'bool':
        '''bool: 'DoesTighteningTechniqueExceedYieldPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DoesTighteningTechniqueExceedYieldPoint

    @property
    def tightening_technique(self) -> '_1285.TighteningTechniques':
        '''TighteningTechniques: 'TighteningTechnique' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.TighteningTechnique)
        return constructor.new(_1285.TighteningTechniques)(value) if value is not None else None

    @tightening_technique.setter
    def tightening_technique(self, value: '_1285.TighteningTechniques'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.TighteningTechnique = value

    @property
    def bolt(self) -> '_1275.DetailedBoltDesign':
        '''DetailedBoltDesign: 'Bolt' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1275.DetailedBoltDesign)(self.wrapped.Bolt) if self.wrapped.Bolt is not None else None

    @property
    def load_vector(self) -> 'Vector3D':
        '''Vector3D: 'LoadVector' is the original name of this property.'''

        value = conversion.pn_to_mp_vector3d(self.wrapped.LoadVector)
        return value

    @load_vector.setter
    def load_vector(self, value: 'Vector3D'):
        value = value if value else None
        value = conversion.mp_to_pn_vector3d(value)
        self.wrapped.LoadVector = value

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def output_default_report_to(self, file_path: 'str'):
        ''' 'OutputDefaultReportTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputDefaultReportTo(file_path if file_path else '')

    def get_default_report_with_encoded_images(self) -> 'str':
        ''' 'GetDefaultReportWithEncodedImages' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.GetDefaultReportWithEncodedImages()
        return method_result

    def output_active_report_to(self, file_path: 'str'):
        ''' 'OutputActiveReportTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputActiveReportTo(file_path if file_path else '')

    def output_active_report_as_text_to(self, file_path: 'str'):
        ''' 'OutputActiveReportAsTextTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputActiveReportAsTextTo(file_path if file_path else '')

    def get_active_report_with_encoded_images(self) -> 'str':
        ''' 'GetActiveReportWithEncodedImages' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.GetActiveReportWithEncodedImages()
        return method_result

    def output_named_report_to(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportTo' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportTo(report_name if report_name else '', file_path if file_path else '')

    def output_named_report_as_masta_report(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportAsMastaReport' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportAsMastaReport(report_name if report_name else '', file_path if file_path else '')

    def output_named_report_as_text_to(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportAsTextTo' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportAsTextTo(report_name if report_name else '', file_path if file_path else '')

    def get_named_report_with_encoded_images(self, report_name: 'str') -> 'str':
        ''' 'GetNamedReportWithEncodedImages' is the original name of this method.

        Args:
            report_name (str)

        Returns:
            str
        '''

        report_name = str(report_name)
        method_result = self.wrapped.GetNamedReportWithEncodedImages(report_name if report_name else '')
        return method_result
