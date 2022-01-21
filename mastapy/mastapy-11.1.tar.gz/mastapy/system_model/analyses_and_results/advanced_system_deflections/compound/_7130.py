'''_7130.py

AssemblyCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model import _2176, _2215
from mastapy._internal import constructor, conversion
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _6997
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import (
    _7131, _7133, _7136, _7142,
    _7143, _7144, _7149, _7154,
    _7164, _7166, _7168, _7172,
    _7178, _7179, _7180, _7187,
    _7194, _7197, _7198, _7199,
    _7201, _7203, _7208, _7209,
    _7210, _7219, _7212, _7214,
    _7218, _7224, _7225, _7230,
    _7233, _7236, _7240, _7244,
    _7248, _7251, _7123
)
from mastapy._internal.python_net import python_net_import

_ASSEMBLY_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'AssemblyCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('AssemblyCompoundAdvancedSystemDeflection',)


class AssemblyCompoundAdvancedSystemDeflection(_7123.AbstractAssemblyCompoundAdvancedSystemDeflection):
    '''AssemblyCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _ASSEMBLY_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AssemblyCompoundAdvancedSystemDeflection.TYPE'):
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
    def assembly_analysis_cases_ready(self) -> 'List[_6997.AssemblyAdvancedSystemDeflection]':
        '''List[AssemblyAdvancedSystemDeflection]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_6997.AssemblyAdvancedSystemDeflection))
        return value

    @property
    def bearings(self) -> 'List[_7131.BearingCompoundAdvancedSystemDeflection]':
        '''List[BearingCompoundAdvancedSystemDeflection]: 'Bearings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Bearings, constructor.new(_7131.BearingCompoundAdvancedSystemDeflection))
        return value

    @property
    def belt_drives(self) -> 'List[_7133.BeltDriveCompoundAdvancedSystemDeflection]':
        '''List[BeltDriveCompoundAdvancedSystemDeflection]: 'BeltDrives' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BeltDrives, constructor.new(_7133.BeltDriveCompoundAdvancedSystemDeflection))
        return value

    @property
    def bevel_differential_gear_sets(self) -> 'List[_7136.BevelDifferentialGearSetCompoundAdvancedSystemDeflection]':
        '''List[BevelDifferentialGearSetCompoundAdvancedSystemDeflection]: 'BevelDifferentialGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialGearSets, constructor.new(_7136.BevelDifferentialGearSetCompoundAdvancedSystemDeflection))
        return value

    @property
    def bolts(self) -> 'List[_7142.BoltCompoundAdvancedSystemDeflection]':
        '''List[BoltCompoundAdvancedSystemDeflection]: 'Bolts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Bolts, constructor.new(_7142.BoltCompoundAdvancedSystemDeflection))
        return value

    @property
    def bolted_joints(self) -> 'List[_7143.BoltedJointCompoundAdvancedSystemDeflection]':
        '''List[BoltedJointCompoundAdvancedSystemDeflection]: 'BoltedJoints' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BoltedJoints, constructor.new(_7143.BoltedJointCompoundAdvancedSystemDeflection))
        return value

    @property
    def clutches(self) -> 'List[_7144.ClutchCompoundAdvancedSystemDeflection]':
        '''List[ClutchCompoundAdvancedSystemDeflection]: 'Clutches' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Clutches, constructor.new(_7144.ClutchCompoundAdvancedSystemDeflection))
        return value

    @property
    def concept_couplings(self) -> 'List[_7149.ConceptCouplingCompoundAdvancedSystemDeflection]':
        '''List[ConceptCouplingCompoundAdvancedSystemDeflection]: 'ConceptCouplings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptCouplings, constructor.new(_7149.ConceptCouplingCompoundAdvancedSystemDeflection))
        return value

    @property
    def concept_gear_sets(self) -> 'List[_7154.ConceptGearSetCompoundAdvancedSystemDeflection]':
        '''List[ConceptGearSetCompoundAdvancedSystemDeflection]: 'ConceptGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptGearSets, constructor.new(_7154.ConceptGearSetCompoundAdvancedSystemDeflection))
        return value

    @property
    def cv_ts(self) -> 'List[_7164.CVTCompoundAdvancedSystemDeflection]':
        '''List[CVTCompoundAdvancedSystemDeflection]: 'CVTs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CVTs, constructor.new(_7164.CVTCompoundAdvancedSystemDeflection))
        return value

    @property
    def cycloidal_assemblies(self) -> 'List[_7166.CycloidalAssemblyCompoundAdvancedSystemDeflection]':
        '''List[CycloidalAssemblyCompoundAdvancedSystemDeflection]: 'CycloidalAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CycloidalAssemblies, constructor.new(_7166.CycloidalAssemblyCompoundAdvancedSystemDeflection))
        return value

    @property
    def cycloidal_discs(self) -> 'List[_7168.CycloidalDiscCompoundAdvancedSystemDeflection]':
        '''List[CycloidalDiscCompoundAdvancedSystemDeflection]: 'CycloidalDiscs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CycloidalDiscs, constructor.new(_7168.CycloidalDiscCompoundAdvancedSystemDeflection))
        return value

    @property
    def cylindrical_gear_sets(self) -> 'List[_7172.CylindricalGearSetCompoundAdvancedSystemDeflection]':
        '''List[CylindricalGearSetCompoundAdvancedSystemDeflection]: 'CylindricalGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGearSets, constructor.new(_7172.CylindricalGearSetCompoundAdvancedSystemDeflection))
        return value

    @property
    def face_gear_sets(self) -> 'List[_7178.FaceGearSetCompoundAdvancedSystemDeflection]':
        '''List[FaceGearSetCompoundAdvancedSystemDeflection]: 'FaceGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearSets, constructor.new(_7178.FaceGearSetCompoundAdvancedSystemDeflection))
        return value

    @property
    def fe_parts(self) -> 'List[_7179.FEPartCompoundAdvancedSystemDeflection]':
        '''List[FEPartCompoundAdvancedSystemDeflection]: 'FEParts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FEParts, constructor.new(_7179.FEPartCompoundAdvancedSystemDeflection))
        return value

    @property
    def flexible_pin_assemblies(self) -> 'List[_7180.FlexiblePinAssemblyCompoundAdvancedSystemDeflection]':
        '''List[FlexiblePinAssemblyCompoundAdvancedSystemDeflection]: 'FlexiblePinAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FlexiblePinAssemblies, constructor.new(_7180.FlexiblePinAssemblyCompoundAdvancedSystemDeflection))
        return value

    @property
    def hypoid_gear_sets(self) -> 'List[_7187.HypoidGearSetCompoundAdvancedSystemDeflection]':
        '''List[HypoidGearSetCompoundAdvancedSystemDeflection]: 'HypoidGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearSets, constructor.new(_7187.HypoidGearSetCompoundAdvancedSystemDeflection))
        return value

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_sets(self) -> 'List[_7194.KlingelnbergCycloPalloidHypoidGearSetCompoundAdvancedSystemDeflection]':
        '''List[KlingelnbergCycloPalloidHypoidGearSetCompoundAdvancedSystemDeflection]: 'KlingelnbergCycloPalloidHypoidGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidGearSets, constructor.new(_7194.KlingelnbergCycloPalloidHypoidGearSetCompoundAdvancedSystemDeflection))
        return value

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_sets(self) -> 'List[_7197.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundAdvancedSystemDeflection]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearSetCompoundAdvancedSystemDeflection]: 'KlingelnbergCycloPalloidSpiralBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelGearSets, constructor.new(_7197.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundAdvancedSystemDeflection))
        return value

    @property
    def mass_discs(self) -> 'List[_7198.MassDiscCompoundAdvancedSystemDeflection]':
        '''List[MassDiscCompoundAdvancedSystemDeflection]: 'MassDiscs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MassDiscs, constructor.new(_7198.MassDiscCompoundAdvancedSystemDeflection))
        return value

    @property
    def measurement_components(self) -> 'List[_7199.MeasurementComponentCompoundAdvancedSystemDeflection]':
        '''List[MeasurementComponentCompoundAdvancedSystemDeflection]: 'MeasurementComponents' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeasurementComponents, constructor.new(_7199.MeasurementComponentCompoundAdvancedSystemDeflection))
        return value

    @property
    def oil_seals(self) -> 'List[_7201.OilSealCompoundAdvancedSystemDeflection]':
        '''List[OilSealCompoundAdvancedSystemDeflection]: 'OilSeals' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.OilSeals, constructor.new(_7201.OilSealCompoundAdvancedSystemDeflection))
        return value

    @property
    def part_to_part_shear_couplings(self) -> 'List[_7203.PartToPartShearCouplingCompoundAdvancedSystemDeflection]':
        '''List[PartToPartShearCouplingCompoundAdvancedSystemDeflection]: 'PartToPartShearCouplings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PartToPartShearCouplings, constructor.new(_7203.PartToPartShearCouplingCompoundAdvancedSystemDeflection))
        return value

    @property
    def planet_carriers(self) -> 'List[_7208.PlanetCarrierCompoundAdvancedSystemDeflection]':
        '''List[PlanetCarrierCompoundAdvancedSystemDeflection]: 'PlanetCarriers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PlanetCarriers, constructor.new(_7208.PlanetCarrierCompoundAdvancedSystemDeflection))
        return value

    @property
    def point_loads(self) -> 'List[_7209.PointLoadCompoundAdvancedSystemDeflection]':
        '''List[PointLoadCompoundAdvancedSystemDeflection]: 'PointLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PointLoads, constructor.new(_7209.PointLoadCompoundAdvancedSystemDeflection))
        return value

    @property
    def power_loads(self) -> 'List[_7210.PowerLoadCompoundAdvancedSystemDeflection]':
        '''List[PowerLoadCompoundAdvancedSystemDeflection]: 'PowerLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PowerLoads, constructor.new(_7210.PowerLoadCompoundAdvancedSystemDeflection))
        return value

    @property
    def shaft_hub_connections(self) -> 'List[_7219.ShaftHubConnectionCompoundAdvancedSystemDeflection]':
        '''List[ShaftHubConnectionCompoundAdvancedSystemDeflection]: 'ShaftHubConnections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ShaftHubConnections, constructor.new(_7219.ShaftHubConnectionCompoundAdvancedSystemDeflection))
        return value

    @property
    def ring_pins(self) -> 'List[_7212.RingPinsCompoundAdvancedSystemDeflection]':
        '''List[RingPinsCompoundAdvancedSystemDeflection]: 'RingPins' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RingPins, constructor.new(_7212.RingPinsCompoundAdvancedSystemDeflection))
        return value

    @property
    def rolling_ring_assemblies(self) -> 'List[_7214.RollingRingAssemblyCompoundAdvancedSystemDeflection]':
        '''List[RollingRingAssemblyCompoundAdvancedSystemDeflection]: 'RollingRingAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RollingRingAssemblies, constructor.new(_7214.RollingRingAssemblyCompoundAdvancedSystemDeflection))
        return value

    @property
    def shafts(self) -> 'List[_7218.ShaftCompoundAdvancedSystemDeflection]':
        '''List[ShaftCompoundAdvancedSystemDeflection]: 'Shafts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Shafts, constructor.new(_7218.ShaftCompoundAdvancedSystemDeflection))
        return value

    @property
    def spiral_bevel_gear_sets(self) -> 'List[_7224.SpiralBevelGearSetCompoundAdvancedSystemDeflection]':
        '''List[SpiralBevelGearSetCompoundAdvancedSystemDeflection]: 'SpiralBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelGearSets, constructor.new(_7224.SpiralBevelGearSetCompoundAdvancedSystemDeflection))
        return value

    @property
    def spring_dampers(self) -> 'List[_7225.SpringDamperCompoundAdvancedSystemDeflection]':
        '''List[SpringDamperCompoundAdvancedSystemDeflection]: 'SpringDampers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpringDampers, constructor.new(_7225.SpringDamperCompoundAdvancedSystemDeflection))
        return value

    @property
    def straight_bevel_diff_gear_sets(self) -> 'List[_7230.StraightBevelDiffGearSetCompoundAdvancedSystemDeflection]':
        '''List[StraightBevelDiffGearSetCompoundAdvancedSystemDeflection]: 'StraightBevelDiffGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffGearSets, constructor.new(_7230.StraightBevelDiffGearSetCompoundAdvancedSystemDeflection))
        return value

    @property
    def straight_bevel_gear_sets(self) -> 'List[_7233.StraightBevelGearSetCompoundAdvancedSystemDeflection]':
        '''List[StraightBevelGearSetCompoundAdvancedSystemDeflection]: 'StraightBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelGearSets, constructor.new(_7233.StraightBevelGearSetCompoundAdvancedSystemDeflection))
        return value

    @property
    def synchronisers(self) -> 'List[_7236.SynchroniserCompoundAdvancedSystemDeflection]':
        '''List[SynchroniserCompoundAdvancedSystemDeflection]: 'Synchronisers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Synchronisers, constructor.new(_7236.SynchroniserCompoundAdvancedSystemDeflection))
        return value

    @property
    def torque_converters(self) -> 'List[_7240.TorqueConverterCompoundAdvancedSystemDeflection]':
        '''List[TorqueConverterCompoundAdvancedSystemDeflection]: 'TorqueConverters' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.TorqueConverters, constructor.new(_7240.TorqueConverterCompoundAdvancedSystemDeflection))
        return value

    @property
    def unbalanced_masses(self) -> 'List[_7244.UnbalancedMassCompoundAdvancedSystemDeflection]':
        '''List[UnbalancedMassCompoundAdvancedSystemDeflection]: 'UnbalancedMasses' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.UnbalancedMasses, constructor.new(_7244.UnbalancedMassCompoundAdvancedSystemDeflection))
        return value

    @property
    def worm_gear_sets(self) -> 'List[_7248.WormGearSetCompoundAdvancedSystemDeflection]':
        '''List[WormGearSetCompoundAdvancedSystemDeflection]: 'WormGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearSets, constructor.new(_7248.WormGearSetCompoundAdvancedSystemDeflection))
        return value

    @property
    def zerol_bevel_gear_sets(self) -> 'List[_7251.ZerolBevelGearSetCompoundAdvancedSystemDeflection]':
        '''List[ZerolBevelGearSetCompoundAdvancedSystemDeflection]: 'ZerolBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelGearSets, constructor.new(_7251.ZerolBevelGearSetCompoundAdvancedSystemDeflection))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_6997.AssemblyAdvancedSystemDeflection]':
        '''List[AssemblyAdvancedSystemDeflection]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_6997.AssemblyAdvancedSystemDeflection))
        return value
