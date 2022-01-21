'''_4827.py

AssemblyModalAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2176, _2215
from mastapy._internal import constructor, conversion
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.static_loads import _6533, _6666
from mastapy.system_model.analyses_and_results.system_deflections import _2432, _2535
from mastapy.system_model.analyses_and_results.modal_analyses import (
    _4877, _4828, _4830, _4833,
    _4840, _4839, _4843, _4848,
    _4851, _4862, _4864, _4866,
    _4870, _4876, _4878, _4886,
    _4893, _4896, _4897, _4898,
    _4903, _4908, _4911, _4912,
    _4913, _4921, _4915, _4917,
    _4922, _4928, _4931, _4934,
    _4937, _4941, _4945, _4948,
    _4957, _4960, _4820
)
from mastapy.system_model.analyses_and_results.modal_analyses.reporting import _4961
from mastapy._internal.python_net import python_net_import

_ASSEMBLY_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses', 'AssemblyModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('AssemblyModalAnalysis',)


class AssemblyModalAnalysis(_4820.AbstractAssemblyModalAnalysis):
    '''AssemblyModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _ASSEMBLY_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AssemblyModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2176.Assembly':
        '''Assembly: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2176.Assembly.TYPE not in self.wrapped.AssemblyDesign.__class__.__mro__:
            raise CastException('Failed to cast assembly_design to Assembly. Expected: {}.'.format(self.wrapped.AssemblyDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AssemblyDesign.__class__)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6533.AssemblyLoadCase':
        '''AssemblyLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6533.AssemblyLoadCase.TYPE not in self.wrapped.AssemblyLoadCase.__class__.__mro__:
            raise CastException('Failed to cast assembly_load_case to AssemblyLoadCase. Expected: {}.'.format(self.wrapped.AssemblyLoadCase.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AssemblyLoadCase.__class__)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def system_deflection_results(self) -> '_2432.AssemblySystemDeflection':
        '''AssemblySystemDeflection: 'SystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2432.AssemblySystemDeflection.TYPE not in self.wrapped.SystemDeflectionResults.__class__.__mro__:
            raise CastException('Failed to cast system_deflection_results to AssemblySystemDeflection. Expected: {}.'.format(self.wrapped.SystemDeflectionResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SystemDeflectionResults.__class__)(self.wrapped.SystemDeflectionResults) if self.wrapped.SystemDeflectionResults is not None else None

    @property
    def full_fe_meshes_for_calculating_modes(self) -> 'List[_4877.FEPartModalAnalysis]':
        '''List[FEPartModalAnalysis]: 'FullFEMeshesForCalculatingModes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FullFEMeshesForCalculatingModes, constructor.new(_4877.FEPartModalAnalysis))
        return value

    @property
    def calculate_full_fe_results_by_mode(self) -> 'List[_4961.CalculateFullFEResultsForMode]':
        '''List[CalculateFullFEResultsForMode]: 'CalculateFullFEResultsByMode' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CalculateFullFEResultsByMode, constructor.new(_4961.CalculateFullFEResultsForMode))
        return value

    @property
    def bearings(self) -> 'List[_4828.BearingModalAnalysis]':
        '''List[BearingModalAnalysis]: 'Bearings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Bearings, constructor.new(_4828.BearingModalAnalysis))
        return value

    @property
    def belt_drives(self) -> 'List[_4830.BeltDriveModalAnalysis]':
        '''List[BeltDriveModalAnalysis]: 'BeltDrives' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BeltDrives, constructor.new(_4830.BeltDriveModalAnalysis))
        return value

    @property
    def bevel_differential_gear_sets(self) -> 'List[_4833.BevelDifferentialGearSetModalAnalysis]':
        '''List[BevelDifferentialGearSetModalAnalysis]: 'BevelDifferentialGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialGearSets, constructor.new(_4833.BevelDifferentialGearSetModalAnalysis))
        return value

    @property
    def bolts(self) -> 'List[_4840.BoltModalAnalysis]':
        '''List[BoltModalAnalysis]: 'Bolts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Bolts, constructor.new(_4840.BoltModalAnalysis))
        return value

    @property
    def bolted_joints(self) -> 'List[_4839.BoltedJointModalAnalysis]':
        '''List[BoltedJointModalAnalysis]: 'BoltedJoints' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BoltedJoints, constructor.new(_4839.BoltedJointModalAnalysis))
        return value

    @property
    def clutches(self) -> 'List[_4843.ClutchModalAnalysis]':
        '''List[ClutchModalAnalysis]: 'Clutches' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Clutches, constructor.new(_4843.ClutchModalAnalysis))
        return value

    @property
    def concept_couplings(self) -> 'List[_4848.ConceptCouplingModalAnalysis]':
        '''List[ConceptCouplingModalAnalysis]: 'ConceptCouplings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptCouplings, constructor.new(_4848.ConceptCouplingModalAnalysis))
        return value

    @property
    def concept_gear_sets(self) -> 'List[_4851.ConceptGearSetModalAnalysis]':
        '''List[ConceptGearSetModalAnalysis]: 'ConceptGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptGearSets, constructor.new(_4851.ConceptGearSetModalAnalysis))
        return value

    @property
    def cv_ts(self) -> 'List[_4862.CVTModalAnalysis]':
        '''List[CVTModalAnalysis]: 'CVTs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CVTs, constructor.new(_4862.CVTModalAnalysis))
        return value

    @property
    def cycloidal_assemblies(self) -> 'List[_4864.CycloidalAssemblyModalAnalysis]':
        '''List[CycloidalAssemblyModalAnalysis]: 'CycloidalAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CycloidalAssemblies, constructor.new(_4864.CycloidalAssemblyModalAnalysis))
        return value

    @property
    def cycloidal_discs(self) -> 'List[_4866.CycloidalDiscModalAnalysis]':
        '''List[CycloidalDiscModalAnalysis]: 'CycloidalDiscs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CycloidalDiscs, constructor.new(_4866.CycloidalDiscModalAnalysis))
        return value

    @property
    def cylindrical_gear_sets(self) -> 'List[_4870.CylindricalGearSetModalAnalysis]':
        '''List[CylindricalGearSetModalAnalysis]: 'CylindricalGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGearSets, constructor.new(_4870.CylindricalGearSetModalAnalysis))
        return value

    @property
    def face_gear_sets(self) -> 'List[_4876.FaceGearSetModalAnalysis]':
        '''List[FaceGearSetModalAnalysis]: 'FaceGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearSets, constructor.new(_4876.FaceGearSetModalAnalysis))
        return value

    @property
    def fe_parts(self) -> 'List[_4877.FEPartModalAnalysis]':
        '''List[FEPartModalAnalysis]: 'FEParts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FEParts, constructor.new(_4877.FEPartModalAnalysis))
        return value

    @property
    def flexible_pin_assemblies(self) -> 'List[_4878.FlexiblePinAssemblyModalAnalysis]':
        '''List[FlexiblePinAssemblyModalAnalysis]: 'FlexiblePinAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FlexiblePinAssemblies, constructor.new(_4878.FlexiblePinAssemblyModalAnalysis))
        return value

    @property
    def hypoid_gear_sets(self) -> 'List[_4886.HypoidGearSetModalAnalysis]':
        '''List[HypoidGearSetModalAnalysis]: 'HypoidGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearSets, constructor.new(_4886.HypoidGearSetModalAnalysis))
        return value

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_sets(self) -> 'List[_4893.KlingelnbergCycloPalloidHypoidGearSetModalAnalysis]':
        '''List[KlingelnbergCycloPalloidHypoidGearSetModalAnalysis]: 'KlingelnbergCycloPalloidHypoidGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidGearSets, constructor.new(_4893.KlingelnbergCycloPalloidHypoidGearSetModalAnalysis))
        return value

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_sets(self) -> 'List[_4896.KlingelnbergCycloPalloidSpiralBevelGearSetModalAnalysis]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearSetModalAnalysis]: 'KlingelnbergCycloPalloidSpiralBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelGearSets, constructor.new(_4896.KlingelnbergCycloPalloidSpiralBevelGearSetModalAnalysis))
        return value

    @property
    def mass_discs(self) -> 'List[_4897.MassDiscModalAnalysis]':
        '''List[MassDiscModalAnalysis]: 'MassDiscs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MassDiscs, constructor.new(_4897.MassDiscModalAnalysis))
        return value

    @property
    def measurement_components(self) -> 'List[_4898.MeasurementComponentModalAnalysis]':
        '''List[MeasurementComponentModalAnalysis]: 'MeasurementComponents' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeasurementComponents, constructor.new(_4898.MeasurementComponentModalAnalysis))
        return value

    @property
    def oil_seals(self) -> 'List[_4903.OilSealModalAnalysis]':
        '''List[OilSealModalAnalysis]: 'OilSeals' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.OilSeals, constructor.new(_4903.OilSealModalAnalysis))
        return value

    @property
    def part_to_part_shear_couplings(self) -> 'List[_4908.PartToPartShearCouplingModalAnalysis]':
        '''List[PartToPartShearCouplingModalAnalysis]: 'PartToPartShearCouplings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PartToPartShearCouplings, constructor.new(_4908.PartToPartShearCouplingModalAnalysis))
        return value

    @property
    def planet_carriers(self) -> 'List[_4911.PlanetCarrierModalAnalysis]':
        '''List[PlanetCarrierModalAnalysis]: 'PlanetCarriers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PlanetCarriers, constructor.new(_4911.PlanetCarrierModalAnalysis))
        return value

    @property
    def point_loads(self) -> 'List[_4912.PointLoadModalAnalysis]':
        '''List[PointLoadModalAnalysis]: 'PointLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PointLoads, constructor.new(_4912.PointLoadModalAnalysis))
        return value

    @property
    def power_loads(self) -> 'List[_4913.PowerLoadModalAnalysis]':
        '''List[PowerLoadModalAnalysis]: 'PowerLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PowerLoads, constructor.new(_4913.PowerLoadModalAnalysis))
        return value

    @property
    def shaft_hub_connections(self) -> 'List[_4921.ShaftHubConnectionModalAnalysis]':
        '''List[ShaftHubConnectionModalAnalysis]: 'ShaftHubConnections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ShaftHubConnections, constructor.new(_4921.ShaftHubConnectionModalAnalysis))
        return value

    @property
    def ring_pins(self) -> 'List[_4915.RingPinsModalAnalysis]':
        '''List[RingPinsModalAnalysis]: 'RingPins' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RingPins, constructor.new(_4915.RingPinsModalAnalysis))
        return value

    @property
    def rolling_ring_assemblies(self) -> 'List[_4917.RollingRingAssemblyModalAnalysis]':
        '''List[RollingRingAssemblyModalAnalysis]: 'RollingRingAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RollingRingAssemblies, constructor.new(_4917.RollingRingAssemblyModalAnalysis))
        return value

    @property
    def shafts(self) -> 'List[_4922.ShaftModalAnalysis]':
        '''List[ShaftModalAnalysis]: 'Shafts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Shafts, constructor.new(_4922.ShaftModalAnalysis))
        return value

    @property
    def spiral_bevel_gear_sets(self) -> 'List[_4928.SpiralBevelGearSetModalAnalysis]':
        '''List[SpiralBevelGearSetModalAnalysis]: 'SpiralBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelGearSets, constructor.new(_4928.SpiralBevelGearSetModalAnalysis))
        return value

    @property
    def spring_dampers(self) -> 'List[_4931.SpringDamperModalAnalysis]':
        '''List[SpringDamperModalAnalysis]: 'SpringDampers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpringDampers, constructor.new(_4931.SpringDamperModalAnalysis))
        return value

    @property
    def straight_bevel_diff_gear_sets(self) -> 'List[_4934.StraightBevelDiffGearSetModalAnalysis]':
        '''List[StraightBevelDiffGearSetModalAnalysis]: 'StraightBevelDiffGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffGearSets, constructor.new(_4934.StraightBevelDiffGearSetModalAnalysis))
        return value

    @property
    def straight_bevel_gear_sets(self) -> 'List[_4937.StraightBevelGearSetModalAnalysis]':
        '''List[StraightBevelGearSetModalAnalysis]: 'StraightBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelGearSets, constructor.new(_4937.StraightBevelGearSetModalAnalysis))
        return value

    @property
    def synchronisers(self) -> 'List[_4941.SynchroniserModalAnalysis]':
        '''List[SynchroniserModalAnalysis]: 'Synchronisers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Synchronisers, constructor.new(_4941.SynchroniserModalAnalysis))
        return value

    @property
    def torque_converters(self) -> 'List[_4945.TorqueConverterModalAnalysis]':
        '''List[TorqueConverterModalAnalysis]: 'TorqueConverters' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.TorqueConverters, constructor.new(_4945.TorqueConverterModalAnalysis))
        return value

    @property
    def unbalanced_masses(self) -> 'List[_4948.UnbalancedMassModalAnalysis]':
        '''List[UnbalancedMassModalAnalysis]: 'UnbalancedMasses' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.UnbalancedMasses, constructor.new(_4948.UnbalancedMassModalAnalysis))
        return value

    @property
    def worm_gear_sets(self) -> 'List[_4957.WormGearSetModalAnalysis]':
        '''List[WormGearSetModalAnalysis]: 'WormGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearSets, constructor.new(_4957.WormGearSetModalAnalysis))
        return value

    @property
    def zerol_bevel_gear_sets(self) -> 'List[_4960.ZerolBevelGearSetModalAnalysis]':
        '''List[ZerolBevelGearSetModalAnalysis]: 'ZerolBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelGearSets, constructor.new(_4960.ZerolBevelGearSetModalAnalysis))
        return value

    def calculate_all_selected_strain_and_kinetic_energies(self):
        ''' 'CalculateAllSelectedStrainAndKineticEnergies' is the original name of this method.'''

        self.wrapped.CalculateAllSelectedStrainAndKineticEnergies()

    def calculate_all_strain_and_kinetic_energies(self):
        ''' 'CalculateAllStrainAndKineticEnergies' is the original name of this method.'''

        self.wrapped.CalculateAllStrainAndKineticEnergies()
