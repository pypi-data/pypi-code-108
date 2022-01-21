'''_2474.py

CylindricalGearMeshSystemDeflection
'''


from typing import List

from PIL.Image import Image

from mastapy._internal import constructor, conversion
from mastapy.utility.report import _1559
from mastapy.system_model.connections_and_sockets.gears import _2051
from mastapy.system_model.analyses_and_results.static_loads import _6577
from mastapy.system_model.analyses_and_results.power_flows import _3813
from mastapy.gears.rating.cylindrical import _421
from mastapy.system_model.analyses_and_results.system_deflections import (
    _2480, _2481, _2482, _2485,
    _2484, _2494
)
from mastapy._internal.cast_exception import CastException
from mastapy.nodal_analysis import _52
from mastapy.system_model.analyses_and_results.system_deflections.reporting import _2580
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_MESH_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'CylindricalGearMeshSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearMeshSystemDeflection',)


class CylindricalGearMeshSystemDeflection(_2494.GearMeshSystemDeflection):
    '''CylindricalGearMeshSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_MESH_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearMeshSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def is_in_contact(self) -> 'bool':
        '''bool: 'IsInContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IsInContact

    @property
    def pinion_torque_for_ltca(self) -> 'float':
        '''float: 'PinionTorqueForLTCA' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionTorqueForLTCA

    @property
    def separation(self) -> 'float':
        '''float: 'Separation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Separation

    @property
    def separation_to_inactive_flank(self) -> 'float':
        '''float: 'SeparationToInactiveFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SeparationToInactiveFlank

    @property
    def load_in_loa_from_ltca(self) -> 'float':
        '''float: 'LoadInLOAFromLTCA' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadInLOAFromLTCA

    @property
    def transmission_error_including_backlash(self) -> 'float':
        '''float: 'TransmissionErrorIncludingBacklash' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransmissionErrorIncludingBacklash

    @property
    def transmission_error_no_backlash(self) -> 'float':
        '''float: 'TransmissionErrorNoBacklash' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransmissionErrorNoBacklash

    @property
    def angular_misalignment_for_harmonic_analysis(self) -> 'float':
        '''float: 'AngularMisalignmentForHarmonicAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AngularMisalignmentForHarmonicAnalysis

    @property
    def average_interference_normal_to_the_flank(self) -> 'float':
        '''float: 'AverageInterferenceNormalToTheFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageInterferenceNormalToTheFlank

    @property
    def estimated_operating_tooth_temperature(self) -> 'float':
        '''float: 'EstimatedOperatingToothTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EstimatedOperatingToothTemperature

    @property
    def minimum_operating_backlash(self) -> 'float':
        '''float: 'MinimumOperatingBacklash' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumOperatingBacklash

    @property
    def maximum_operating_backlash(self) -> 'float':
        '''float: 'MaximumOperatingBacklash' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumOperatingBacklash

    @property
    def average_operating_backlash(self) -> 'float':
        '''float: 'AverageOperatingBacklash' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageOperatingBacklash

    @property
    def change_in_operating_backlash_due_to_thermal_effects(self) -> 'float':
        '''float: 'ChangeInOperatingBacklashDueToThermalEffects' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ChangeInOperatingBacklashDueToThermalEffects

    @property
    def change_in_backlash_due_to_tooth_expansion(self) -> 'float':
        '''float: 'ChangeInBacklashDueToToothExpansion' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ChangeInBacklashDueToToothExpansion

    @property
    def minimum_operating_centre_distance(self) -> 'float':
        '''float: 'MinimumOperatingCentreDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumOperatingCentreDistance

    @property
    def maximum_operating_centre_distance(self) -> 'float':
        '''float: 'MaximumOperatingCentreDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumOperatingCentreDistance

    @property
    def smallest_effective_operating_centre_distance(self) -> 'float':
        '''float: 'SmallestEffectiveOperatingCentreDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SmallestEffectiveOperatingCentreDistance

    @property
    def minimum_change_in_centre_distance_due_to_misalignment(self) -> 'float':
        '''float: 'MinimumChangeInCentreDistanceDueToMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumChangeInCentreDistanceDueToMisalignment

    @property
    def maximum_change_in_centre_distance_due_to_misalignment(self) -> 'float':
        '''float: 'MaximumChangeInCentreDistanceDueToMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumChangeInCentreDistanceDueToMisalignment

    @property
    def node_pair_changes_in_operating_centre_distance_due_to_misalignment(self) -> 'List[float]':
        '''List[float]: 'NodePairChangesInOperatingCentreDistanceDueToMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.NodePairChangesInOperatingCentreDistanceDueToMisalignment)
        return value

    @property
    def node_pair_transverse_separations_for_ltca(self) -> 'List[float]':
        '''List[float]: 'NodePairTransverseSeparationsForLTCA' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.NodePairTransverseSeparationsForLTCA)
        return value

    @property
    def minimum_change_in_centre_distance(self) -> 'float':
        '''float: 'MinimumChangeInCentreDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumChangeInCentreDistance

    @property
    def maximum_change_in_centre_distance(self) -> 'float':
        '''float: 'MaximumChangeInCentreDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumChangeInCentreDistance

    @property
    def minimum_operating_transverse_contact_ratio(self) -> 'float':
        '''float: 'MinimumOperatingTransverseContactRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumOperatingTransverseContactRatio

    @property
    def maximum_operating_transverse_contact_ratio(self) -> 'float':
        '''float: 'MaximumOperatingTransverseContactRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumOperatingTransverseContactRatio

    @property
    def chart_of_effective_change_in_operating_centre_distance(self) -> 'Image':
        '''Image: 'ChartOfEffectiveChangeInOperatingCentreDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.ChartOfEffectiveChangeInOperatingCentreDistance)
        return value

    @property
    def chart_of_misalignment_in_transverse_line_of_action(self) -> '_1559.LegacyChartDefinition':
        '''LegacyChartDefinition: 'ChartOfMisalignmentInTransverseLineOfAction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1559.LegacyChartDefinition)(self.wrapped.ChartOfMisalignmentInTransverseLineOfAction) if self.wrapped.ChartOfMisalignmentInTransverseLineOfAction is not None else None

    @property
    def signed_root_mean_square_planetary_equivalent_misalignment(self) -> 'float':
        '''float: 'SignedRootMeanSquarePlanetaryEquivalentMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SignedRootMeanSquarePlanetaryEquivalentMisalignment

    @property
    def worst_planetary_misalignment(self) -> 'float':
        '''float: 'WorstPlanetaryMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WorstPlanetaryMisalignment

    @property
    def calculated_worst_load_sharing_factor(self) -> 'float':
        '''float: 'CalculatedWorstLoadSharingFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CalculatedWorstLoadSharingFactor

    @property
    def calculated_load_sharing_factor(self) -> 'float':
        '''float: 'CalculatedLoadSharingFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CalculatedLoadSharingFactor

    @property
    def gear_mesh_tilt_stiffness_method(self) -> 'str':
        '''str: 'GearMeshTiltStiffnessMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearMeshTiltStiffnessMethod

    @property
    def crowning_for_tilt_stiffness_gear_a(self) -> 'float':
        '''float: 'CrowningForTiltStiffnessGearA' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CrowningForTiltStiffnessGearA

    @property
    def crowning_for_tilt_stiffness_gear_b(self) -> 'float':
        '''float: 'CrowningForTiltStiffnessGearB' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CrowningForTiltStiffnessGearB

    @property
    def linear_relief_for_tilt_stiffness_gear_a(self) -> 'float':
        '''float: 'LinearReliefForTiltStiffnessGearA' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LinearReliefForTiltStiffnessGearA

    @property
    def linear_relief_for_tilt_stiffness_gear_b(self) -> 'float':
        '''float: 'LinearReliefForTiltStiffnessGearB' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LinearReliefForTiltStiffnessGearB

    @property
    def connection_design(self) -> '_2051.CylindricalGearMesh':
        '''CylindricalGearMesh: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2051.CylindricalGearMesh)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def connection_load_case(self) -> '_6577.CylindricalGearMeshLoadCase':
        '''CylindricalGearMeshLoadCase: 'ConnectionLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6577.CylindricalGearMeshLoadCase)(self.wrapped.ConnectionLoadCase) if self.wrapped.ConnectionLoadCase is not None else None

    @property
    def power_flow_results(self) -> '_3813.CylindricalGearMeshPowerFlow':
        '''CylindricalGearMeshPowerFlow: 'PowerFlowResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_3813.CylindricalGearMeshPowerFlow)(self.wrapped.PowerFlowResults) if self.wrapped.PowerFlowResults is not None else None

    @property
    def rating(self) -> '_421.CylindricalGearMeshRating':
        '''CylindricalGearMeshRating: 'Rating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_421.CylindricalGearMeshRating)(self.wrapped.Rating) if self.wrapped.Rating is not None else None

    @property
    def component_detailed_analysis(self) -> '_421.CylindricalGearMeshRating':
        '''CylindricalGearMeshRating: 'ComponentDetailedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_421.CylindricalGearMeshRating)(self.wrapped.ComponentDetailedAnalysis) if self.wrapped.ComponentDetailedAnalysis is not None else None

    @property
    def gear_a(self) -> '_2480.CylindricalGearSystemDeflection':
        '''CylindricalGearSystemDeflection: 'GearA' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2480.CylindricalGearSystemDeflection.TYPE not in self.wrapped.GearA.__class__.__mro__:
            raise CastException('Failed to cast gear_a to CylindricalGearSystemDeflection. Expected: {}.'.format(self.wrapped.GearA.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearA.__class__)(self.wrapped.GearA) if self.wrapped.GearA is not None else None

    @property
    def gear_a_of_type_cylindrical_gear_system_deflection_timestep(self) -> '_2481.CylindricalGearSystemDeflectionTimestep':
        '''CylindricalGearSystemDeflectionTimestep: 'GearA' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2481.CylindricalGearSystemDeflectionTimestep.TYPE not in self.wrapped.GearA.__class__.__mro__:
            raise CastException('Failed to cast gear_a to CylindricalGearSystemDeflectionTimestep. Expected: {}.'.format(self.wrapped.GearA.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearA.__class__)(self.wrapped.GearA) if self.wrapped.GearA is not None else None

    @property
    def gear_a_of_type_cylindrical_gear_system_deflection_with_ltca_results(self) -> '_2482.CylindricalGearSystemDeflectionWithLTCAResults':
        '''CylindricalGearSystemDeflectionWithLTCAResults: 'GearA' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2482.CylindricalGearSystemDeflectionWithLTCAResults.TYPE not in self.wrapped.GearA.__class__.__mro__:
            raise CastException('Failed to cast gear_a to CylindricalGearSystemDeflectionWithLTCAResults. Expected: {}.'.format(self.wrapped.GearA.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearA.__class__)(self.wrapped.GearA) if self.wrapped.GearA is not None else None

    @property
    def gear_a_of_type_cylindrical_planet_gear_system_deflection(self) -> '_2485.CylindricalPlanetGearSystemDeflection':
        '''CylindricalPlanetGearSystemDeflection: 'GearA' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2485.CylindricalPlanetGearSystemDeflection.TYPE not in self.wrapped.GearA.__class__.__mro__:
            raise CastException('Failed to cast gear_a to CylindricalPlanetGearSystemDeflection. Expected: {}.'.format(self.wrapped.GearA.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearA.__class__)(self.wrapped.GearA) if self.wrapped.GearA is not None else None

    @property
    def gear_b(self) -> '_2480.CylindricalGearSystemDeflection':
        '''CylindricalGearSystemDeflection: 'GearB' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2480.CylindricalGearSystemDeflection.TYPE not in self.wrapped.GearB.__class__.__mro__:
            raise CastException('Failed to cast gear_b to CylindricalGearSystemDeflection. Expected: {}.'.format(self.wrapped.GearB.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearB.__class__)(self.wrapped.GearB) if self.wrapped.GearB is not None else None

    @property
    def gear_b_of_type_cylindrical_gear_system_deflection_timestep(self) -> '_2481.CylindricalGearSystemDeflectionTimestep':
        '''CylindricalGearSystemDeflectionTimestep: 'GearB' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2481.CylindricalGearSystemDeflectionTimestep.TYPE not in self.wrapped.GearB.__class__.__mro__:
            raise CastException('Failed to cast gear_b to CylindricalGearSystemDeflectionTimestep. Expected: {}.'.format(self.wrapped.GearB.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearB.__class__)(self.wrapped.GearB) if self.wrapped.GearB is not None else None

    @property
    def gear_b_of_type_cylindrical_gear_system_deflection_with_ltca_results(self) -> '_2482.CylindricalGearSystemDeflectionWithLTCAResults':
        '''CylindricalGearSystemDeflectionWithLTCAResults: 'GearB' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2482.CylindricalGearSystemDeflectionWithLTCAResults.TYPE not in self.wrapped.GearB.__class__.__mro__:
            raise CastException('Failed to cast gear_b to CylindricalGearSystemDeflectionWithLTCAResults. Expected: {}.'.format(self.wrapped.GearB.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearB.__class__)(self.wrapped.GearB) if self.wrapped.GearB is not None else None

    @property
    def gear_b_of_type_cylindrical_planet_gear_system_deflection(self) -> '_2485.CylindricalPlanetGearSystemDeflection':
        '''CylindricalPlanetGearSystemDeflection: 'GearB' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2485.CylindricalPlanetGearSystemDeflection.TYPE not in self.wrapped.GearB.__class__.__mro__:
            raise CastException('Failed to cast gear_b to CylindricalPlanetGearSystemDeflection. Expected: {}.'.format(self.wrapped.GearB.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearB.__class__)(self.wrapped.GearB) if self.wrapped.GearB is not None else None

    @property
    def misalignment_data(self) -> '_52.CylindricalMisalignmentCalculator':
        '''CylindricalMisalignmentCalculator: 'MisalignmentData' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_52.CylindricalMisalignmentCalculator)(self.wrapped.MisalignmentData) if self.wrapped.MisalignmentData is not None else None

    @property
    def misalignment_data_left_flank(self) -> '_52.CylindricalMisalignmentCalculator':
        '''CylindricalMisalignmentCalculator: 'MisalignmentDataLeftFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_52.CylindricalMisalignmentCalculator)(self.wrapped.MisalignmentDataLeftFlank) if self.wrapped.MisalignmentDataLeftFlank is not None else None

    @property
    def misalignment_data_right_flank(self) -> '_52.CylindricalMisalignmentCalculator':
        '''CylindricalMisalignmentCalculator: 'MisalignmentDataRightFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_52.CylindricalMisalignmentCalculator)(self.wrapped.MisalignmentDataRightFlank) if self.wrapped.MisalignmentDataRightFlank is not None else None

    @property
    def planetaries(self) -> 'List[CylindricalGearMeshSystemDeflection]':
        '''List[CylindricalGearMeshSystemDeflection]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(CylindricalGearMeshSystemDeflection))
        return value

    @property
    def cylindrical_gears(self) -> 'List[_2480.CylindricalGearSystemDeflection]':
        '''List[CylindricalGearSystemDeflection]: 'CylindricalGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGears, constructor.new(_2480.CylindricalGearSystemDeflection))
        return value

    @property
    def cylindrical_meshed_gear_system_deflections(self) -> 'List[_2484.CylindricalMeshedGearSystemDeflection]':
        '''List[CylindricalMeshedGearSystemDeflection]: 'CylindricalMeshedGearSystemDeflections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalMeshedGearSystemDeflections, constructor.new(_2484.CylindricalMeshedGearSystemDeflection))
        return value

    @property
    def mesh_deflections_left_flank(self) -> 'List[_2580.MeshDeflectionResults]':
        '''List[MeshDeflectionResults]: 'MeshDeflectionsLeftFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeshDeflectionsLeftFlank, constructor.new(_2580.MeshDeflectionResults))
        return value

    @property
    def mesh_deflections_right_flank(self) -> 'List[_2580.MeshDeflectionResults]':
        '''List[MeshDeflectionResults]: 'MeshDeflectionsRightFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeshDeflectionsRightFlank, constructor.new(_2580.MeshDeflectionResults))
        return value
