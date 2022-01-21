'''_6997.py

AssemblyAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model import _2176, _2215
from mastapy._internal import constructor, conversion
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.static_loads import _6533, _6666
from mastapy.system_model.analyses_and_results.advanced_system_deflections import (
    _6998, _7000, _7003, _7009,
    _7010, _7011, _7016, _7021,
    _7031, _7034, _7035, _7040,
    _7047, _7048, _7049, _7056,
    _7063, _7066, _7068, _7069,
    _7071, _7073, _7078, _7079,
    _7080, _7089, _7082, _7085,
    _7088, _7094, _7095, _7100,
    _7103, _7106, _7110, _7115,
    _7119, _7122, _6987
)
from mastapy.system_model.analyses_and_results.system_deflections import _2432
from mastapy._internal.python_net import python_net_import

_ASSEMBLY_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections', 'AssemblyAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('AssemblyAdvancedSystemDeflection',)


class AssemblyAdvancedSystemDeflection(_6987.AbstractAssemblyAdvancedSystemDeflection):
    '''AssemblyAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _ASSEMBLY_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AssemblyAdvancedSystemDeflection.TYPE'):
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
    def bearings(self) -> 'List[_6998.BearingAdvancedSystemDeflection]':
        '''List[BearingAdvancedSystemDeflection]: 'Bearings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Bearings, constructor.new(_6998.BearingAdvancedSystemDeflection))
        return value

    @property
    def belt_drives(self) -> 'List[_7000.BeltDriveAdvancedSystemDeflection]':
        '''List[BeltDriveAdvancedSystemDeflection]: 'BeltDrives' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BeltDrives, constructor.new(_7000.BeltDriveAdvancedSystemDeflection))
        return value

    @property
    def bevel_differential_gear_sets(self) -> 'List[_7003.BevelDifferentialGearSetAdvancedSystemDeflection]':
        '''List[BevelDifferentialGearSetAdvancedSystemDeflection]: 'BevelDifferentialGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialGearSets, constructor.new(_7003.BevelDifferentialGearSetAdvancedSystemDeflection))
        return value

    @property
    def bolts(self) -> 'List[_7009.BoltAdvancedSystemDeflection]':
        '''List[BoltAdvancedSystemDeflection]: 'Bolts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Bolts, constructor.new(_7009.BoltAdvancedSystemDeflection))
        return value

    @property
    def bolted_joints(self) -> 'List[_7010.BoltedJointAdvancedSystemDeflection]':
        '''List[BoltedJointAdvancedSystemDeflection]: 'BoltedJoints' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BoltedJoints, constructor.new(_7010.BoltedJointAdvancedSystemDeflection))
        return value

    @property
    def clutches(self) -> 'List[_7011.ClutchAdvancedSystemDeflection]':
        '''List[ClutchAdvancedSystemDeflection]: 'Clutches' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Clutches, constructor.new(_7011.ClutchAdvancedSystemDeflection))
        return value

    @property
    def concept_couplings(self) -> 'List[_7016.ConceptCouplingAdvancedSystemDeflection]':
        '''List[ConceptCouplingAdvancedSystemDeflection]: 'ConceptCouplings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptCouplings, constructor.new(_7016.ConceptCouplingAdvancedSystemDeflection))
        return value

    @property
    def concept_gear_sets(self) -> 'List[_7021.ConceptGearSetAdvancedSystemDeflection]':
        '''List[ConceptGearSetAdvancedSystemDeflection]: 'ConceptGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptGearSets, constructor.new(_7021.ConceptGearSetAdvancedSystemDeflection))
        return value

    @property
    def cv_ts(self) -> 'List[_7031.CVTAdvancedSystemDeflection]':
        '''List[CVTAdvancedSystemDeflection]: 'CVTs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CVTs, constructor.new(_7031.CVTAdvancedSystemDeflection))
        return value

    @property
    def cycloidal_assemblies(self) -> 'List[_7034.CycloidalAssemblyAdvancedSystemDeflection]':
        '''List[CycloidalAssemblyAdvancedSystemDeflection]: 'CycloidalAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CycloidalAssemblies, constructor.new(_7034.CycloidalAssemblyAdvancedSystemDeflection))
        return value

    @property
    def cycloidal_discs(self) -> 'List[_7035.CycloidalDiscAdvancedSystemDeflection]':
        '''List[CycloidalDiscAdvancedSystemDeflection]: 'CycloidalDiscs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CycloidalDiscs, constructor.new(_7035.CycloidalDiscAdvancedSystemDeflection))
        return value

    @property
    def cylindrical_gear_sets(self) -> 'List[_7040.CylindricalGearSetAdvancedSystemDeflection]':
        '''List[CylindricalGearSetAdvancedSystemDeflection]: 'CylindricalGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGearSets, constructor.new(_7040.CylindricalGearSetAdvancedSystemDeflection))
        return value

    @property
    def face_gear_sets(self) -> 'List[_7047.FaceGearSetAdvancedSystemDeflection]':
        '''List[FaceGearSetAdvancedSystemDeflection]: 'FaceGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearSets, constructor.new(_7047.FaceGearSetAdvancedSystemDeflection))
        return value

    @property
    def fe_parts(self) -> 'List[_7048.FEPartAdvancedSystemDeflection]':
        '''List[FEPartAdvancedSystemDeflection]: 'FEParts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FEParts, constructor.new(_7048.FEPartAdvancedSystemDeflection))
        return value

    @property
    def flexible_pin_assemblies(self) -> 'List[_7049.FlexiblePinAssemblyAdvancedSystemDeflection]':
        '''List[FlexiblePinAssemblyAdvancedSystemDeflection]: 'FlexiblePinAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FlexiblePinAssemblies, constructor.new(_7049.FlexiblePinAssemblyAdvancedSystemDeflection))
        return value

    @property
    def hypoid_gear_sets(self) -> 'List[_7056.HypoidGearSetAdvancedSystemDeflection]':
        '''List[HypoidGearSetAdvancedSystemDeflection]: 'HypoidGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearSets, constructor.new(_7056.HypoidGearSetAdvancedSystemDeflection))
        return value

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_sets(self) -> 'List[_7063.KlingelnbergCycloPalloidHypoidGearSetAdvancedSystemDeflection]':
        '''List[KlingelnbergCycloPalloidHypoidGearSetAdvancedSystemDeflection]: 'KlingelnbergCycloPalloidHypoidGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidGearSets, constructor.new(_7063.KlingelnbergCycloPalloidHypoidGearSetAdvancedSystemDeflection))
        return value

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_sets(self) -> 'List[_7066.KlingelnbergCycloPalloidSpiralBevelGearSetAdvancedSystemDeflection]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearSetAdvancedSystemDeflection]: 'KlingelnbergCycloPalloidSpiralBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelGearSets, constructor.new(_7066.KlingelnbergCycloPalloidSpiralBevelGearSetAdvancedSystemDeflection))
        return value

    @property
    def mass_discs(self) -> 'List[_7068.MassDiscAdvancedSystemDeflection]':
        '''List[MassDiscAdvancedSystemDeflection]: 'MassDiscs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MassDiscs, constructor.new(_7068.MassDiscAdvancedSystemDeflection))
        return value

    @property
    def measurement_components(self) -> 'List[_7069.MeasurementComponentAdvancedSystemDeflection]':
        '''List[MeasurementComponentAdvancedSystemDeflection]: 'MeasurementComponents' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeasurementComponents, constructor.new(_7069.MeasurementComponentAdvancedSystemDeflection))
        return value

    @property
    def oil_seals(self) -> 'List[_7071.OilSealAdvancedSystemDeflection]':
        '''List[OilSealAdvancedSystemDeflection]: 'OilSeals' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.OilSeals, constructor.new(_7071.OilSealAdvancedSystemDeflection))
        return value

    @property
    def part_to_part_shear_couplings(self) -> 'List[_7073.PartToPartShearCouplingAdvancedSystemDeflection]':
        '''List[PartToPartShearCouplingAdvancedSystemDeflection]: 'PartToPartShearCouplings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PartToPartShearCouplings, constructor.new(_7073.PartToPartShearCouplingAdvancedSystemDeflection))
        return value

    @property
    def planet_carriers(self) -> 'List[_7078.PlanetCarrierAdvancedSystemDeflection]':
        '''List[PlanetCarrierAdvancedSystemDeflection]: 'PlanetCarriers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PlanetCarriers, constructor.new(_7078.PlanetCarrierAdvancedSystemDeflection))
        return value

    @property
    def point_loads(self) -> 'List[_7079.PointLoadAdvancedSystemDeflection]':
        '''List[PointLoadAdvancedSystemDeflection]: 'PointLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PointLoads, constructor.new(_7079.PointLoadAdvancedSystemDeflection))
        return value

    @property
    def power_loads(self) -> 'List[_7080.PowerLoadAdvancedSystemDeflection]':
        '''List[PowerLoadAdvancedSystemDeflection]: 'PowerLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PowerLoads, constructor.new(_7080.PowerLoadAdvancedSystemDeflection))
        return value

    @property
    def shaft_hub_connections(self) -> 'List[_7089.ShaftHubConnectionAdvancedSystemDeflection]':
        '''List[ShaftHubConnectionAdvancedSystemDeflection]: 'ShaftHubConnections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ShaftHubConnections, constructor.new(_7089.ShaftHubConnectionAdvancedSystemDeflection))
        return value

    @property
    def ring_pins(self) -> 'List[_7082.RingPinsAdvancedSystemDeflection]':
        '''List[RingPinsAdvancedSystemDeflection]: 'RingPins' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RingPins, constructor.new(_7082.RingPinsAdvancedSystemDeflection))
        return value

    @property
    def rolling_ring_assemblies(self) -> 'List[_7085.RollingRingAssemblyAdvancedSystemDeflection]':
        '''List[RollingRingAssemblyAdvancedSystemDeflection]: 'RollingRingAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RollingRingAssemblies, constructor.new(_7085.RollingRingAssemblyAdvancedSystemDeflection))
        return value

    @property
    def shafts(self) -> 'List[_7088.ShaftAdvancedSystemDeflection]':
        '''List[ShaftAdvancedSystemDeflection]: 'Shafts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Shafts, constructor.new(_7088.ShaftAdvancedSystemDeflection))
        return value

    @property
    def spiral_bevel_gear_sets(self) -> 'List[_7094.SpiralBevelGearSetAdvancedSystemDeflection]':
        '''List[SpiralBevelGearSetAdvancedSystemDeflection]: 'SpiralBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelGearSets, constructor.new(_7094.SpiralBevelGearSetAdvancedSystemDeflection))
        return value

    @property
    def spring_dampers(self) -> 'List[_7095.SpringDamperAdvancedSystemDeflection]':
        '''List[SpringDamperAdvancedSystemDeflection]: 'SpringDampers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpringDampers, constructor.new(_7095.SpringDamperAdvancedSystemDeflection))
        return value

    @property
    def straight_bevel_diff_gear_sets(self) -> 'List[_7100.StraightBevelDiffGearSetAdvancedSystemDeflection]':
        '''List[StraightBevelDiffGearSetAdvancedSystemDeflection]: 'StraightBevelDiffGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffGearSets, constructor.new(_7100.StraightBevelDiffGearSetAdvancedSystemDeflection))
        return value

    @property
    def straight_bevel_gear_sets(self) -> 'List[_7103.StraightBevelGearSetAdvancedSystemDeflection]':
        '''List[StraightBevelGearSetAdvancedSystemDeflection]: 'StraightBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelGearSets, constructor.new(_7103.StraightBevelGearSetAdvancedSystemDeflection))
        return value

    @property
    def synchronisers(self) -> 'List[_7106.SynchroniserAdvancedSystemDeflection]':
        '''List[SynchroniserAdvancedSystemDeflection]: 'Synchronisers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Synchronisers, constructor.new(_7106.SynchroniserAdvancedSystemDeflection))
        return value

    @property
    def torque_converters(self) -> 'List[_7110.TorqueConverterAdvancedSystemDeflection]':
        '''List[TorqueConverterAdvancedSystemDeflection]: 'TorqueConverters' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.TorqueConverters, constructor.new(_7110.TorqueConverterAdvancedSystemDeflection))
        return value

    @property
    def unbalanced_masses(self) -> 'List[_7115.UnbalancedMassAdvancedSystemDeflection]':
        '''List[UnbalancedMassAdvancedSystemDeflection]: 'UnbalancedMasses' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.UnbalancedMasses, constructor.new(_7115.UnbalancedMassAdvancedSystemDeflection))
        return value

    @property
    def worm_gear_sets(self) -> 'List[_7119.WormGearSetAdvancedSystemDeflection]':
        '''List[WormGearSetAdvancedSystemDeflection]: 'WormGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearSets, constructor.new(_7119.WormGearSetAdvancedSystemDeflection))
        return value

    @property
    def zerol_bevel_gear_sets(self) -> 'List[_7122.ZerolBevelGearSetAdvancedSystemDeflection]':
        '''List[ZerolBevelGearSetAdvancedSystemDeflection]: 'ZerolBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelGearSets, constructor.new(_7122.ZerolBevelGearSetAdvancedSystemDeflection))
        return value

    @property
    def assembly_system_deflection_results(self) -> 'List[_2432.AssemblySystemDeflection]':
        '''List[AssemblySystemDeflection]: 'AssemblySystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblySystemDeflectionResults, constructor.new(_2432.AssemblySystemDeflection))
        return value
