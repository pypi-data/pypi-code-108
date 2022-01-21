'''_6865.py

AssemblyCompoundAdvancedTimeSteppingAnalysisForModulation
'''


from typing import List

from mastapy.system_model.part_model import _2176, _2215
from mastapy._internal import constructor, conversion
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import _6734
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation.compound import (
    _6866, _6868, _6871, _6877,
    _6878, _6879, _6884, _6889,
    _6899, _6901, _6903, _6907,
    _6913, _6914, _6915, _6922,
    _6929, _6932, _6933, _6934,
    _6936, _6938, _6943, _6944,
    _6945, _6954, _6947, _6949,
    _6953, _6959, _6960, _6965,
    _6968, _6971, _6975, _6979,
    _6983, _6986, _6858
)
from mastapy._internal.python_net import python_net_import

_ASSEMBLY_COMPOUND_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation.Compound', 'AssemblyCompoundAdvancedTimeSteppingAnalysisForModulation')


__docformat__ = 'restructuredtext en'
__all__ = ('AssemblyCompoundAdvancedTimeSteppingAnalysisForModulation',)


class AssemblyCompoundAdvancedTimeSteppingAnalysisForModulation(_6858.AbstractAssemblyCompoundAdvancedTimeSteppingAnalysisForModulation):
    '''AssemblyCompoundAdvancedTimeSteppingAnalysisForModulation

    This is a mastapy class.
    '''

    TYPE = _ASSEMBLY_COMPOUND_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AssemblyCompoundAdvancedTimeSteppingAnalysisForModulation.TYPE'):
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
    def assembly_analysis_cases_ready(self) -> 'List[_6734.AssemblyAdvancedTimeSteppingAnalysisForModulation]':
        '''List[AssemblyAdvancedTimeSteppingAnalysisForModulation]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_6734.AssemblyAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def bearings(self) -> 'List[_6866.BearingCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[BearingCompoundAdvancedTimeSteppingAnalysisForModulation]: 'Bearings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Bearings, constructor.new(_6866.BearingCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def belt_drives(self) -> 'List[_6868.BeltDriveCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[BeltDriveCompoundAdvancedTimeSteppingAnalysisForModulation]: 'BeltDrives' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BeltDrives, constructor.new(_6868.BeltDriveCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def bevel_differential_gear_sets(self) -> 'List[_6871.BevelDifferentialGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[BevelDifferentialGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]: 'BevelDifferentialGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialGearSets, constructor.new(_6871.BevelDifferentialGearSetCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def bolts(self) -> 'List[_6877.BoltCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[BoltCompoundAdvancedTimeSteppingAnalysisForModulation]: 'Bolts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Bolts, constructor.new(_6877.BoltCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def bolted_joints(self) -> 'List[_6878.BoltedJointCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[BoltedJointCompoundAdvancedTimeSteppingAnalysisForModulation]: 'BoltedJoints' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BoltedJoints, constructor.new(_6878.BoltedJointCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def clutches(self) -> 'List[_6879.ClutchCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[ClutchCompoundAdvancedTimeSteppingAnalysisForModulation]: 'Clutches' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Clutches, constructor.new(_6879.ClutchCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def concept_couplings(self) -> 'List[_6884.ConceptCouplingCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[ConceptCouplingCompoundAdvancedTimeSteppingAnalysisForModulation]: 'ConceptCouplings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptCouplings, constructor.new(_6884.ConceptCouplingCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def concept_gear_sets(self) -> 'List[_6889.ConceptGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[ConceptGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]: 'ConceptGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptGearSets, constructor.new(_6889.ConceptGearSetCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def cv_ts(self) -> 'List[_6899.CVTCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[CVTCompoundAdvancedTimeSteppingAnalysisForModulation]: 'CVTs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CVTs, constructor.new(_6899.CVTCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def cycloidal_assemblies(self) -> 'List[_6901.CycloidalAssemblyCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[CycloidalAssemblyCompoundAdvancedTimeSteppingAnalysisForModulation]: 'CycloidalAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CycloidalAssemblies, constructor.new(_6901.CycloidalAssemblyCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def cycloidal_discs(self) -> 'List[_6903.CycloidalDiscCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[CycloidalDiscCompoundAdvancedTimeSteppingAnalysisForModulation]: 'CycloidalDiscs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CycloidalDiscs, constructor.new(_6903.CycloidalDiscCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def cylindrical_gear_sets(self) -> 'List[_6907.CylindricalGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[CylindricalGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]: 'CylindricalGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGearSets, constructor.new(_6907.CylindricalGearSetCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def face_gear_sets(self) -> 'List[_6913.FaceGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[FaceGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]: 'FaceGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearSets, constructor.new(_6913.FaceGearSetCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def fe_parts(self) -> 'List[_6914.FEPartCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[FEPartCompoundAdvancedTimeSteppingAnalysisForModulation]: 'FEParts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FEParts, constructor.new(_6914.FEPartCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def flexible_pin_assemblies(self) -> 'List[_6915.FlexiblePinAssemblyCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[FlexiblePinAssemblyCompoundAdvancedTimeSteppingAnalysisForModulation]: 'FlexiblePinAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FlexiblePinAssemblies, constructor.new(_6915.FlexiblePinAssemblyCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def hypoid_gear_sets(self) -> 'List[_6922.HypoidGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[HypoidGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]: 'HypoidGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearSets, constructor.new(_6922.HypoidGearSetCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_sets(self) -> 'List[_6929.KlingelnbergCycloPalloidHypoidGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[KlingelnbergCycloPalloidHypoidGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]: 'KlingelnbergCycloPalloidHypoidGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidGearSets, constructor.new(_6929.KlingelnbergCycloPalloidHypoidGearSetCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_sets(self) -> 'List[_6932.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]: 'KlingelnbergCycloPalloidSpiralBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelGearSets, constructor.new(_6932.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def mass_discs(self) -> 'List[_6933.MassDiscCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[MassDiscCompoundAdvancedTimeSteppingAnalysisForModulation]: 'MassDiscs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MassDiscs, constructor.new(_6933.MassDiscCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def measurement_components(self) -> 'List[_6934.MeasurementComponentCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[MeasurementComponentCompoundAdvancedTimeSteppingAnalysisForModulation]: 'MeasurementComponents' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeasurementComponents, constructor.new(_6934.MeasurementComponentCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def oil_seals(self) -> 'List[_6936.OilSealCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[OilSealCompoundAdvancedTimeSteppingAnalysisForModulation]: 'OilSeals' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.OilSeals, constructor.new(_6936.OilSealCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def part_to_part_shear_couplings(self) -> 'List[_6938.PartToPartShearCouplingCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[PartToPartShearCouplingCompoundAdvancedTimeSteppingAnalysisForModulation]: 'PartToPartShearCouplings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PartToPartShearCouplings, constructor.new(_6938.PartToPartShearCouplingCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def planet_carriers(self) -> 'List[_6943.PlanetCarrierCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[PlanetCarrierCompoundAdvancedTimeSteppingAnalysisForModulation]: 'PlanetCarriers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PlanetCarriers, constructor.new(_6943.PlanetCarrierCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def point_loads(self) -> 'List[_6944.PointLoadCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[PointLoadCompoundAdvancedTimeSteppingAnalysisForModulation]: 'PointLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PointLoads, constructor.new(_6944.PointLoadCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def power_loads(self) -> 'List[_6945.PowerLoadCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[PowerLoadCompoundAdvancedTimeSteppingAnalysisForModulation]: 'PowerLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PowerLoads, constructor.new(_6945.PowerLoadCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def shaft_hub_connections(self) -> 'List[_6954.ShaftHubConnectionCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[ShaftHubConnectionCompoundAdvancedTimeSteppingAnalysisForModulation]: 'ShaftHubConnections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ShaftHubConnections, constructor.new(_6954.ShaftHubConnectionCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def ring_pins(self) -> 'List[_6947.RingPinsCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[RingPinsCompoundAdvancedTimeSteppingAnalysisForModulation]: 'RingPins' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RingPins, constructor.new(_6947.RingPinsCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def rolling_ring_assemblies(self) -> 'List[_6949.RollingRingAssemblyCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[RollingRingAssemblyCompoundAdvancedTimeSteppingAnalysisForModulation]: 'RollingRingAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RollingRingAssemblies, constructor.new(_6949.RollingRingAssemblyCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def shafts(self) -> 'List[_6953.ShaftCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[ShaftCompoundAdvancedTimeSteppingAnalysisForModulation]: 'Shafts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Shafts, constructor.new(_6953.ShaftCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def spiral_bevel_gear_sets(self) -> 'List[_6959.SpiralBevelGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[SpiralBevelGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]: 'SpiralBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelGearSets, constructor.new(_6959.SpiralBevelGearSetCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def spring_dampers(self) -> 'List[_6960.SpringDamperCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[SpringDamperCompoundAdvancedTimeSteppingAnalysisForModulation]: 'SpringDampers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpringDampers, constructor.new(_6960.SpringDamperCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def straight_bevel_diff_gear_sets(self) -> 'List[_6965.StraightBevelDiffGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[StraightBevelDiffGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]: 'StraightBevelDiffGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffGearSets, constructor.new(_6965.StraightBevelDiffGearSetCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def straight_bevel_gear_sets(self) -> 'List[_6968.StraightBevelGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[StraightBevelGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]: 'StraightBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelGearSets, constructor.new(_6968.StraightBevelGearSetCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def synchronisers(self) -> 'List[_6971.SynchroniserCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[SynchroniserCompoundAdvancedTimeSteppingAnalysisForModulation]: 'Synchronisers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Synchronisers, constructor.new(_6971.SynchroniserCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def torque_converters(self) -> 'List[_6975.TorqueConverterCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[TorqueConverterCompoundAdvancedTimeSteppingAnalysisForModulation]: 'TorqueConverters' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.TorqueConverters, constructor.new(_6975.TorqueConverterCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def unbalanced_masses(self) -> 'List[_6979.UnbalancedMassCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[UnbalancedMassCompoundAdvancedTimeSteppingAnalysisForModulation]: 'UnbalancedMasses' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.UnbalancedMasses, constructor.new(_6979.UnbalancedMassCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def worm_gear_sets(self) -> 'List[_6983.WormGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[WormGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]: 'WormGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearSets, constructor.new(_6983.WormGearSetCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def zerol_bevel_gear_sets(self) -> 'List[_6986.ZerolBevelGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[ZerolBevelGearSetCompoundAdvancedTimeSteppingAnalysisForModulation]: 'ZerolBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelGearSets, constructor.new(_6986.ZerolBevelGearSetCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_6734.AssemblyAdvancedTimeSteppingAnalysisForModulation]':
        '''List[AssemblyAdvancedTimeSteppingAnalysisForModulation]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_6734.AssemblyAdvancedTimeSteppingAnalysisForModulation))
        return value
