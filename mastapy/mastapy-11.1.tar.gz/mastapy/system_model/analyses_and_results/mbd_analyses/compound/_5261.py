'''_5261.py

AssemblyCompoundMultibodyDynamicsAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2176, _2215
from mastapy._internal import constructor, conversion
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.mbd_analyses import _5110
from mastapy.system_model.analyses_and_results.mbd_analyses.compound import (
    _5262, _5264, _5267, _5273,
    _5274, _5275, _5280, _5285,
    _5295, _5297, _5299, _5303,
    _5309, _5310, _5311, _5318,
    _5325, _5328, _5329, _5330,
    _5332, _5334, _5339, _5340,
    _5341, _5350, _5343, _5345,
    _5349, _5355, _5356, _5361,
    _5364, _5367, _5371, _5375,
    _5379, _5382, _5254
)
from mastapy._internal.python_net import python_net_import

_ASSEMBLY_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Compound', 'AssemblyCompoundMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('AssemblyCompoundMultibodyDynamicsAnalysis',)


class AssemblyCompoundMultibodyDynamicsAnalysis(_5254.AbstractAssemblyCompoundMultibodyDynamicsAnalysis):
    '''AssemblyCompoundMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _ASSEMBLY_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AssemblyCompoundMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2176.Assembly':
        '''Assembly: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2176.Assembly.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to Assembly. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

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
    def assembly_analysis_cases_ready(self) -> 'List[_5110.AssemblyMultibodyDynamicsAnalysis]':
        '''List[AssemblyMultibodyDynamicsAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_5110.AssemblyMultibodyDynamicsAnalysis))
        return value

    @property
    def bearings(self) -> 'List[_5262.BearingCompoundMultibodyDynamicsAnalysis]':
        '''List[BearingCompoundMultibodyDynamicsAnalysis]: 'Bearings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Bearings, constructor.new(_5262.BearingCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def belt_drives(self) -> 'List[_5264.BeltDriveCompoundMultibodyDynamicsAnalysis]':
        '''List[BeltDriveCompoundMultibodyDynamicsAnalysis]: 'BeltDrives' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BeltDrives, constructor.new(_5264.BeltDriveCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def bevel_differential_gear_sets(self) -> 'List[_5267.BevelDifferentialGearSetCompoundMultibodyDynamicsAnalysis]':
        '''List[BevelDifferentialGearSetCompoundMultibodyDynamicsAnalysis]: 'BevelDifferentialGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialGearSets, constructor.new(_5267.BevelDifferentialGearSetCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def bolts(self) -> 'List[_5273.BoltCompoundMultibodyDynamicsAnalysis]':
        '''List[BoltCompoundMultibodyDynamicsAnalysis]: 'Bolts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Bolts, constructor.new(_5273.BoltCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def bolted_joints(self) -> 'List[_5274.BoltedJointCompoundMultibodyDynamicsAnalysis]':
        '''List[BoltedJointCompoundMultibodyDynamicsAnalysis]: 'BoltedJoints' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BoltedJoints, constructor.new(_5274.BoltedJointCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def clutches(self) -> 'List[_5275.ClutchCompoundMultibodyDynamicsAnalysis]':
        '''List[ClutchCompoundMultibodyDynamicsAnalysis]: 'Clutches' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Clutches, constructor.new(_5275.ClutchCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def concept_couplings(self) -> 'List[_5280.ConceptCouplingCompoundMultibodyDynamicsAnalysis]':
        '''List[ConceptCouplingCompoundMultibodyDynamicsAnalysis]: 'ConceptCouplings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptCouplings, constructor.new(_5280.ConceptCouplingCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def concept_gear_sets(self) -> 'List[_5285.ConceptGearSetCompoundMultibodyDynamicsAnalysis]':
        '''List[ConceptGearSetCompoundMultibodyDynamicsAnalysis]: 'ConceptGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptGearSets, constructor.new(_5285.ConceptGearSetCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def cv_ts(self) -> 'List[_5295.CVTCompoundMultibodyDynamicsAnalysis]':
        '''List[CVTCompoundMultibodyDynamicsAnalysis]: 'CVTs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CVTs, constructor.new(_5295.CVTCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def cycloidal_assemblies(self) -> 'List[_5297.CycloidalAssemblyCompoundMultibodyDynamicsAnalysis]':
        '''List[CycloidalAssemblyCompoundMultibodyDynamicsAnalysis]: 'CycloidalAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CycloidalAssemblies, constructor.new(_5297.CycloidalAssemblyCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def cycloidal_discs(self) -> 'List[_5299.CycloidalDiscCompoundMultibodyDynamicsAnalysis]':
        '''List[CycloidalDiscCompoundMultibodyDynamicsAnalysis]: 'CycloidalDiscs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CycloidalDiscs, constructor.new(_5299.CycloidalDiscCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def cylindrical_gear_sets(self) -> 'List[_5303.CylindricalGearSetCompoundMultibodyDynamicsAnalysis]':
        '''List[CylindricalGearSetCompoundMultibodyDynamicsAnalysis]: 'CylindricalGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGearSets, constructor.new(_5303.CylindricalGearSetCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def face_gear_sets(self) -> 'List[_5309.FaceGearSetCompoundMultibodyDynamicsAnalysis]':
        '''List[FaceGearSetCompoundMultibodyDynamicsAnalysis]: 'FaceGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearSets, constructor.new(_5309.FaceGearSetCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def fe_parts(self) -> 'List[_5310.FEPartCompoundMultibodyDynamicsAnalysis]':
        '''List[FEPartCompoundMultibodyDynamicsAnalysis]: 'FEParts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FEParts, constructor.new(_5310.FEPartCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def flexible_pin_assemblies(self) -> 'List[_5311.FlexiblePinAssemblyCompoundMultibodyDynamicsAnalysis]':
        '''List[FlexiblePinAssemblyCompoundMultibodyDynamicsAnalysis]: 'FlexiblePinAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FlexiblePinAssemblies, constructor.new(_5311.FlexiblePinAssemblyCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def hypoid_gear_sets(self) -> 'List[_5318.HypoidGearSetCompoundMultibodyDynamicsAnalysis]':
        '''List[HypoidGearSetCompoundMultibodyDynamicsAnalysis]: 'HypoidGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearSets, constructor.new(_5318.HypoidGearSetCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_sets(self) -> 'List[_5325.KlingelnbergCycloPalloidHypoidGearSetCompoundMultibodyDynamicsAnalysis]':
        '''List[KlingelnbergCycloPalloidHypoidGearSetCompoundMultibodyDynamicsAnalysis]: 'KlingelnbergCycloPalloidHypoidGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidGearSets, constructor.new(_5325.KlingelnbergCycloPalloidHypoidGearSetCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_sets(self) -> 'List[_5328.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundMultibodyDynamicsAnalysis]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearSetCompoundMultibodyDynamicsAnalysis]: 'KlingelnbergCycloPalloidSpiralBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelGearSets, constructor.new(_5328.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def mass_discs(self) -> 'List[_5329.MassDiscCompoundMultibodyDynamicsAnalysis]':
        '''List[MassDiscCompoundMultibodyDynamicsAnalysis]: 'MassDiscs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MassDiscs, constructor.new(_5329.MassDiscCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def measurement_components(self) -> 'List[_5330.MeasurementComponentCompoundMultibodyDynamicsAnalysis]':
        '''List[MeasurementComponentCompoundMultibodyDynamicsAnalysis]: 'MeasurementComponents' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeasurementComponents, constructor.new(_5330.MeasurementComponentCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def oil_seals(self) -> 'List[_5332.OilSealCompoundMultibodyDynamicsAnalysis]':
        '''List[OilSealCompoundMultibodyDynamicsAnalysis]: 'OilSeals' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.OilSeals, constructor.new(_5332.OilSealCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def part_to_part_shear_couplings(self) -> 'List[_5334.PartToPartShearCouplingCompoundMultibodyDynamicsAnalysis]':
        '''List[PartToPartShearCouplingCompoundMultibodyDynamicsAnalysis]: 'PartToPartShearCouplings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PartToPartShearCouplings, constructor.new(_5334.PartToPartShearCouplingCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def planet_carriers(self) -> 'List[_5339.PlanetCarrierCompoundMultibodyDynamicsAnalysis]':
        '''List[PlanetCarrierCompoundMultibodyDynamicsAnalysis]: 'PlanetCarriers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PlanetCarriers, constructor.new(_5339.PlanetCarrierCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def point_loads(self) -> 'List[_5340.PointLoadCompoundMultibodyDynamicsAnalysis]':
        '''List[PointLoadCompoundMultibodyDynamicsAnalysis]: 'PointLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PointLoads, constructor.new(_5340.PointLoadCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def power_loads(self) -> 'List[_5341.PowerLoadCompoundMultibodyDynamicsAnalysis]':
        '''List[PowerLoadCompoundMultibodyDynamicsAnalysis]: 'PowerLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PowerLoads, constructor.new(_5341.PowerLoadCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def shaft_hub_connections(self) -> 'List[_5350.ShaftHubConnectionCompoundMultibodyDynamicsAnalysis]':
        '''List[ShaftHubConnectionCompoundMultibodyDynamicsAnalysis]: 'ShaftHubConnections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ShaftHubConnections, constructor.new(_5350.ShaftHubConnectionCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def ring_pins(self) -> 'List[_5343.RingPinsCompoundMultibodyDynamicsAnalysis]':
        '''List[RingPinsCompoundMultibodyDynamicsAnalysis]: 'RingPins' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RingPins, constructor.new(_5343.RingPinsCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def rolling_ring_assemblies(self) -> 'List[_5345.RollingRingAssemblyCompoundMultibodyDynamicsAnalysis]':
        '''List[RollingRingAssemblyCompoundMultibodyDynamicsAnalysis]: 'RollingRingAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RollingRingAssemblies, constructor.new(_5345.RollingRingAssemblyCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def shafts(self) -> 'List[_5349.ShaftCompoundMultibodyDynamicsAnalysis]':
        '''List[ShaftCompoundMultibodyDynamicsAnalysis]: 'Shafts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Shafts, constructor.new(_5349.ShaftCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def spiral_bevel_gear_sets(self) -> 'List[_5355.SpiralBevelGearSetCompoundMultibodyDynamicsAnalysis]':
        '''List[SpiralBevelGearSetCompoundMultibodyDynamicsAnalysis]: 'SpiralBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelGearSets, constructor.new(_5355.SpiralBevelGearSetCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def spring_dampers(self) -> 'List[_5356.SpringDamperCompoundMultibodyDynamicsAnalysis]':
        '''List[SpringDamperCompoundMultibodyDynamicsAnalysis]: 'SpringDampers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpringDampers, constructor.new(_5356.SpringDamperCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def straight_bevel_diff_gear_sets(self) -> 'List[_5361.StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis]':
        '''List[StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis]: 'StraightBevelDiffGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffGearSets, constructor.new(_5361.StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def straight_bevel_gear_sets(self) -> 'List[_5364.StraightBevelGearSetCompoundMultibodyDynamicsAnalysis]':
        '''List[StraightBevelGearSetCompoundMultibodyDynamicsAnalysis]: 'StraightBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelGearSets, constructor.new(_5364.StraightBevelGearSetCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def synchronisers(self) -> 'List[_5367.SynchroniserCompoundMultibodyDynamicsAnalysis]':
        '''List[SynchroniserCompoundMultibodyDynamicsAnalysis]: 'Synchronisers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Synchronisers, constructor.new(_5367.SynchroniserCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def torque_converters(self) -> 'List[_5371.TorqueConverterCompoundMultibodyDynamicsAnalysis]':
        '''List[TorqueConverterCompoundMultibodyDynamicsAnalysis]: 'TorqueConverters' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.TorqueConverters, constructor.new(_5371.TorqueConverterCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def unbalanced_masses(self) -> 'List[_5375.UnbalancedMassCompoundMultibodyDynamicsAnalysis]':
        '''List[UnbalancedMassCompoundMultibodyDynamicsAnalysis]: 'UnbalancedMasses' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.UnbalancedMasses, constructor.new(_5375.UnbalancedMassCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def worm_gear_sets(self) -> 'List[_5379.WormGearSetCompoundMultibodyDynamicsAnalysis]':
        '''List[WormGearSetCompoundMultibodyDynamicsAnalysis]: 'WormGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearSets, constructor.new(_5379.WormGearSetCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def zerol_bevel_gear_sets(self) -> 'List[_5382.ZerolBevelGearSetCompoundMultibodyDynamicsAnalysis]':
        '''List[ZerolBevelGearSetCompoundMultibodyDynamicsAnalysis]: 'ZerolBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelGearSets, constructor.new(_5382.ZerolBevelGearSetCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_5110.AssemblyMultibodyDynamicsAnalysis]':
        '''List[AssemblyMultibodyDynamicsAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_5110.AssemblyMultibodyDynamicsAnalysis))
        return value
