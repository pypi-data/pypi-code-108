'''_5410.py

AssemblyHarmonicAnalysisOfSingleExcitation
'''


from typing import List

from mastapy.system_model.part_model import _2176, _2215
from mastapy._internal import constructor, conversion
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.static_loads import _6533, _6666
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
    _5411, _5413, _5416, _5423,
    _5422, _5426, _5431, _5434,
    _5444, _5446, _5448, _5452,
    _5458, _5459, _5460, _5468,
    _5475, _5478, _5479, _5480,
    _5482, _5486, _5489, _5490,
    _5491, _5500, _5493, _5495,
    _5499, _5505, _5508, _5511,
    _5514, _5518, _5522, _5525,
    _5529, _5532, _5403
)
from mastapy._internal.python_net import python_net_import

_ASSEMBLY_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation', 'AssemblyHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('AssemblyHarmonicAnalysisOfSingleExcitation',)


class AssemblyHarmonicAnalysisOfSingleExcitation(_5403.AbstractAssemblyHarmonicAnalysisOfSingleExcitation):
    '''AssemblyHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _ASSEMBLY_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AssemblyHarmonicAnalysisOfSingleExcitation.TYPE'):
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
    def bearings(self) -> 'List[_5411.BearingHarmonicAnalysisOfSingleExcitation]':
        '''List[BearingHarmonicAnalysisOfSingleExcitation]: 'Bearings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Bearings, constructor.new(_5411.BearingHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def belt_drives(self) -> 'List[_5413.BeltDriveHarmonicAnalysisOfSingleExcitation]':
        '''List[BeltDriveHarmonicAnalysisOfSingleExcitation]: 'BeltDrives' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BeltDrives, constructor.new(_5413.BeltDriveHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def bevel_differential_gear_sets(self) -> 'List[_5416.BevelDifferentialGearSetHarmonicAnalysisOfSingleExcitation]':
        '''List[BevelDifferentialGearSetHarmonicAnalysisOfSingleExcitation]: 'BevelDifferentialGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialGearSets, constructor.new(_5416.BevelDifferentialGearSetHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def bolts(self) -> 'List[_5423.BoltHarmonicAnalysisOfSingleExcitation]':
        '''List[BoltHarmonicAnalysisOfSingleExcitation]: 'Bolts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Bolts, constructor.new(_5423.BoltHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def bolted_joints(self) -> 'List[_5422.BoltedJointHarmonicAnalysisOfSingleExcitation]':
        '''List[BoltedJointHarmonicAnalysisOfSingleExcitation]: 'BoltedJoints' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BoltedJoints, constructor.new(_5422.BoltedJointHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def clutches(self) -> 'List[_5426.ClutchHarmonicAnalysisOfSingleExcitation]':
        '''List[ClutchHarmonicAnalysisOfSingleExcitation]: 'Clutches' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Clutches, constructor.new(_5426.ClutchHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def concept_couplings(self) -> 'List[_5431.ConceptCouplingHarmonicAnalysisOfSingleExcitation]':
        '''List[ConceptCouplingHarmonicAnalysisOfSingleExcitation]: 'ConceptCouplings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptCouplings, constructor.new(_5431.ConceptCouplingHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def concept_gear_sets(self) -> 'List[_5434.ConceptGearSetHarmonicAnalysisOfSingleExcitation]':
        '''List[ConceptGearSetHarmonicAnalysisOfSingleExcitation]: 'ConceptGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptGearSets, constructor.new(_5434.ConceptGearSetHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def cv_ts(self) -> 'List[_5444.CVTHarmonicAnalysisOfSingleExcitation]':
        '''List[CVTHarmonicAnalysisOfSingleExcitation]: 'CVTs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CVTs, constructor.new(_5444.CVTHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def cycloidal_assemblies(self) -> 'List[_5446.CycloidalAssemblyHarmonicAnalysisOfSingleExcitation]':
        '''List[CycloidalAssemblyHarmonicAnalysisOfSingleExcitation]: 'CycloidalAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CycloidalAssemblies, constructor.new(_5446.CycloidalAssemblyHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def cycloidal_discs(self) -> 'List[_5448.CycloidalDiscHarmonicAnalysisOfSingleExcitation]':
        '''List[CycloidalDiscHarmonicAnalysisOfSingleExcitation]: 'CycloidalDiscs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CycloidalDiscs, constructor.new(_5448.CycloidalDiscHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def cylindrical_gear_sets(self) -> 'List[_5452.CylindricalGearSetHarmonicAnalysisOfSingleExcitation]':
        '''List[CylindricalGearSetHarmonicAnalysisOfSingleExcitation]: 'CylindricalGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGearSets, constructor.new(_5452.CylindricalGearSetHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def face_gear_sets(self) -> 'List[_5458.FaceGearSetHarmonicAnalysisOfSingleExcitation]':
        '''List[FaceGearSetHarmonicAnalysisOfSingleExcitation]: 'FaceGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearSets, constructor.new(_5458.FaceGearSetHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def fe_parts(self) -> 'List[_5459.FEPartHarmonicAnalysisOfSingleExcitation]':
        '''List[FEPartHarmonicAnalysisOfSingleExcitation]: 'FEParts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FEParts, constructor.new(_5459.FEPartHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def flexible_pin_assemblies(self) -> 'List[_5460.FlexiblePinAssemblyHarmonicAnalysisOfSingleExcitation]':
        '''List[FlexiblePinAssemblyHarmonicAnalysisOfSingleExcitation]: 'FlexiblePinAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FlexiblePinAssemblies, constructor.new(_5460.FlexiblePinAssemblyHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def hypoid_gear_sets(self) -> 'List[_5468.HypoidGearSetHarmonicAnalysisOfSingleExcitation]':
        '''List[HypoidGearSetHarmonicAnalysisOfSingleExcitation]: 'HypoidGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearSets, constructor.new(_5468.HypoidGearSetHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_sets(self) -> 'List[_5475.KlingelnbergCycloPalloidHypoidGearSetHarmonicAnalysisOfSingleExcitation]':
        '''List[KlingelnbergCycloPalloidHypoidGearSetHarmonicAnalysisOfSingleExcitation]: 'KlingelnbergCycloPalloidHypoidGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidGearSets, constructor.new(_5475.KlingelnbergCycloPalloidHypoidGearSetHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_sets(self) -> 'List[_5478.KlingelnbergCycloPalloidSpiralBevelGearSetHarmonicAnalysisOfSingleExcitation]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearSetHarmonicAnalysisOfSingleExcitation]: 'KlingelnbergCycloPalloidSpiralBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelGearSets, constructor.new(_5478.KlingelnbergCycloPalloidSpiralBevelGearSetHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def mass_discs(self) -> 'List[_5479.MassDiscHarmonicAnalysisOfSingleExcitation]':
        '''List[MassDiscHarmonicAnalysisOfSingleExcitation]: 'MassDiscs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MassDiscs, constructor.new(_5479.MassDiscHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def measurement_components(self) -> 'List[_5480.MeasurementComponentHarmonicAnalysisOfSingleExcitation]':
        '''List[MeasurementComponentHarmonicAnalysisOfSingleExcitation]: 'MeasurementComponents' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeasurementComponents, constructor.new(_5480.MeasurementComponentHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def oil_seals(self) -> 'List[_5482.OilSealHarmonicAnalysisOfSingleExcitation]':
        '''List[OilSealHarmonicAnalysisOfSingleExcitation]: 'OilSeals' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.OilSeals, constructor.new(_5482.OilSealHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def part_to_part_shear_couplings(self) -> 'List[_5486.PartToPartShearCouplingHarmonicAnalysisOfSingleExcitation]':
        '''List[PartToPartShearCouplingHarmonicAnalysisOfSingleExcitation]: 'PartToPartShearCouplings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PartToPartShearCouplings, constructor.new(_5486.PartToPartShearCouplingHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def planet_carriers(self) -> 'List[_5489.PlanetCarrierHarmonicAnalysisOfSingleExcitation]':
        '''List[PlanetCarrierHarmonicAnalysisOfSingleExcitation]: 'PlanetCarriers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PlanetCarriers, constructor.new(_5489.PlanetCarrierHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def point_loads(self) -> 'List[_5490.PointLoadHarmonicAnalysisOfSingleExcitation]':
        '''List[PointLoadHarmonicAnalysisOfSingleExcitation]: 'PointLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PointLoads, constructor.new(_5490.PointLoadHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def power_loads(self) -> 'List[_5491.PowerLoadHarmonicAnalysisOfSingleExcitation]':
        '''List[PowerLoadHarmonicAnalysisOfSingleExcitation]: 'PowerLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PowerLoads, constructor.new(_5491.PowerLoadHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def shaft_hub_connections(self) -> 'List[_5500.ShaftHubConnectionHarmonicAnalysisOfSingleExcitation]':
        '''List[ShaftHubConnectionHarmonicAnalysisOfSingleExcitation]: 'ShaftHubConnections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ShaftHubConnections, constructor.new(_5500.ShaftHubConnectionHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def ring_pins(self) -> 'List[_5493.RingPinsHarmonicAnalysisOfSingleExcitation]':
        '''List[RingPinsHarmonicAnalysisOfSingleExcitation]: 'RingPins' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RingPins, constructor.new(_5493.RingPinsHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def rolling_ring_assemblies(self) -> 'List[_5495.RollingRingAssemblyHarmonicAnalysisOfSingleExcitation]':
        '''List[RollingRingAssemblyHarmonicAnalysisOfSingleExcitation]: 'RollingRingAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RollingRingAssemblies, constructor.new(_5495.RollingRingAssemblyHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def shafts(self) -> 'List[_5499.ShaftHarmonicAnalysisOfSingleExcitation]':
        '''List[ShaftHarmonicAnalysisOfSingleExcitation]: 'Shafts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Shafts, constructor.new(_5499.ShaftHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def spiral_bevel_gear_sets(self) -> 'List[_5505.SpiralBevelGearSetHarmonicAnalysisOfSingleExcitation]':
        '''List[SpiralBevelGearSetHarmonicAnalysisOfSingleExcitation]: 'SpiralBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelGearSets, constructor.new(_5505.SpiralBevelGearSetHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def spring_dampers(self) -> 'List[_5508.SpringDamperHarmonicAnalysisOfSingleExcitation]':
        '''List[SpringDamperHarmonicAnalysisOfSingleExcitation]: 'SpringDampers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpringDampers, constructor.new(_5508.SpringDamperHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def straight_bevel_diff_gear_sets(self) -> 'List[_5511.StraightBevelDiffGearSetHarmonicAnalysisOfSingleExcitation]':
        '''List[StraightBevelDiffGearSetHarmonicAnalysisOfSingleExcitation]: 'StraightBevelDiffGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffGearSets, constructor.new(_5511.StraightBevelDiffGearSetHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def straight_bevel_gear_sets(self) -> 'List[_5514.StraightBevelGearSetHarmonicAnalysisOfSingleExcitation]':
        '''List[StraightBevelGearSetHarmonicAnalysisOfSingleExcitation]: 'StraightBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelGearSets, constructor.new(_5514.StraightBevelGearSetHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def synchronisers(self) -> 'List[_5518.SynchroniserHarmonicAnalysisOfSingleExcitation]':
        '''List[SynchroniserHarmonicAnalysisOfSingleExcitation]: 'Synchronisers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Synchronisers, constructor.new(_5518.SynchroniserHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def torque_converters(self) -> 'List[_5522.TorqueConverterHarmonicAnalysisOfSingleExcitation]':
        '''List[TorqueConverterHarmonicAnalysisOfSingleExcitation]: 'TorqueConverters' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.TorqueConverters, constructor.new(_5522.TorqueConverterHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def unbalanced_masses(self) -> 'List[_5525.UnbalancedMassHarmonicAnalysisOfSingleExcitation]':
        '''List[UnbalancedMassHarmonicAnalysisOfSingleExcitation]: 'UnbalancedMasses' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.UnbalancedMasses, constructor.new(_5525.UnbalancedMassHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def worm_gear_sets(self) -> 'List[_5529.WormGearSetHarmonicAnalysisOfSingleExcitation]':
        '''List[WormGearSetHarmonicAnalysisOfSingleExcitation]: 'WormGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearSets, constructor.new(_5529.WormGearSetHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def zerol_bevel_gear_sets(self) -> 'List[_5532.ZerolBevelGearSetHarmonicAnalysisOfSingleExcitation]':
        '''List[ZerolBevelGearSetHarmonicAnalysisOfSingleExcitation]: 'ZerolBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelGearSets, constructor.new(_5532.ZerolBevelGearSetHarmonicAnalysisOfSingleExcitation))
        return value
