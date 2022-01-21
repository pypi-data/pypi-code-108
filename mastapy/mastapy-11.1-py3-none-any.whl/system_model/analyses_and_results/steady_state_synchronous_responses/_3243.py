'''_3243.py

AssemblySteadyStateSynchronousResponse
'''


from typing import List

from mastapy.system_model.part_model import _2176, _2215
from mastapy._internal import constructor, conversion
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.static_loads import _6533, _6666
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses import (
    _3244, _3246, _3248, _3256,
    _3255, _3259, _3264, _3266,
    _3278, _3279, _3282, _3284,
    _3291, _3293, _3294, _3300,
    _3307, _3310, _3312, _3313,
    _3315, _3319, _3322, _3323,
    _3324, _3332, _3326, _3328,
    _3333, _3337, _3341, _3346,
    _3349, _3356, _3359, _3361,
    _3364, _3367, _3236
)
from mastapy._internal.python_net import python_net_import

_ASSEMBLY_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses', 'AssemblySteadyStateSynchronousResponse')


__docformat__ = 'restructuredtext en'
__all__ = ('AssemblySteadyStateSynchronousResponse',)


class AssemblySteadyStateSynchronousResponse(_3236.AbstractAssemblySteadyStateSynchronousResponse):
    '''AssemblySteadyStateSynchronousResponse

    This is a mastapy class.
    '''

    TYPE = _ASSEMBLY_STEADY_STATE_SYNCHRONOUS_RESPONSE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AssemblySteadyStateSynchronousResponse.TYPE'):
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
    def bearings(self) -> 'List[_3244.BearingSteadyStateSynchronousResponse]':
        '''List[BearingSteadyStateSynchronousResponse]: 'Bearings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Bearings, constructor.new(_3244.BearingSteadyStateSynchronousResponse))
        return value

    @property
    def belt_drives(self) -> 'List[_3246.BeltDriveSteadyStateSynchronousResponse]':
        '''List[BeltDriveSteadyStateSynchronousResponse]: 'BeltDrives' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BeltDrives, constructor.new(_3246.BeltDriveSteadyStateSynchronousResponse))
        return value

    @property
    def bevel_differential_gear_sets(self) -> 'List[_3248.BevelDifferentialGearSetSteadyStateSynchronousResponse]':
        '''List[BevelDifferentialGearSetSteadyStateSynchronousResponse]: 'BevelDifferentialGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialGearSets, constructor.new(_3248.BevelDifferentialGearSetSteadyStateSynchronousResponse))
        return value

    @property
    def bolts(self) -> 'List[_3256.BoltSteadyStateSynchronousResponse]':
        '''List[BoltSteadyStateSynchronousResponse]: 'Bolts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Bolts, constructor.new(_3256.BoltSteadyStateSynchronousResponse))
        return value

    @property
    def bolted_joints(self) -> 'List[_3255.BoltedJointSteadyStateSynchronousResponse]':
        '''List[BoltedJointSteadyStateSynchronousResponse]: 'BoltedJoints' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BoltedJoints, constructor.new(_3255.BoltedJointSteadyStateSynchronousResponse))
        return value

    @property
    def clutches(self) -> 'List[_3259.ClutchSteadyStateSynchronousResponse]':
        '''List[ClutchSteadyStateSynchronousResponse]: 'Clutches' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Clutches, constructor.new(_3259.ClutchSteadyStateSynchronousResponse))
        return value

    @property
    def concept_couplings(self) -> 'List[_3264.ConceptCouplingSteadyStateSynchronousResponse]':
        '''List[ConceptCouplingSteadyStateSynchronousResponse]: 'ConceptCouplings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptCouplings, constructor.new(_3264.ConceptCouplingSteadyStateSynchronousResponse))
        return value

    @property
    def concept_gear_sets(self) -> 'List[_3266.ConceptGearSetSteadyStateSynchronousResponse]':
        '''List[ConceptGearSetSteadyStateSynchronousResponse]: 'ConceptGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptGearSets, constructor.new(_3266.ConceptGearSetSteadyStateSynchronousResponse))
        return value

    @property
    def cv_ts(self) -> 'List[_3278.CVTSteadyStateSynchronousResponse]':
        '''List[CVTSteadyStateSynchronousResponse]: 'CVTs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CVTs, constructor.new(_3278.CVTSteadyStateSynchronousResponse))
        return value

    @property
    def cycloidal_assemblies(self) -> 'List[_3279.CycloidalAssemblySteadyStateSynchronousResponse]':
        '''List[CycloidalAssemblySteadyStateSynchronousResponse]: 'CycloidalAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CycloidalAssemblies, constructor.new(_3279.CycloidalAssemblySteadyStateSynchronousResponse))
        return value

    @property
    def cycloidal_discs(self) -> 'List[_3282.CycloidalDiscSteadyStateSynchronousResponse]':
        '''List[CycloidalDiscSteadyStateSynchronousResponse]: 'CycloidalDiscs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CycloidalDiscs, constructor.new(_3282.CycloidalDiscSteadyStateSynchronousResponse))
        return value

    @property
    def cylindrical_gear_sets(self) -> 'List[_3284.CylindricalGearSetSteadyStateSynchronousResponse]':
        '''List[CylindricalGearSetSteadyStateSynchronousResponse]: 'CylindricalGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGearSets, constructor.new(_3284.CylindricalGearSetSteadyStateSynchronousResponse))
        return value

    @property
    def face_gear_sets(self) -> 'List[_3291.FaceGearSetSteadyStateSynchronousResponse]':
        '''List[FaceGearSetSteadyStateSynchronousResponse]: 'FaceGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearSets, constructor.new(_3291.FaceGearSetSteadyStateSynchronousResponse))
        return value

    @property
    def fe_parts(self) -> 'List[_3293.FEPartSteadyStateSynchronousResponse]':
        '''List[FEPartSteadyStateSynchronousResponse]: 'FEParts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FEParts, constructor.new(_3293.FEPartSteadyStateSynchronousResponse))
        return value

    @property
    def flexible_pin_assemblies(self) -> 'List[_3294.FlexiblePinAssemblySteadyStateSynchronousResponse]':
        '''List[FlexiblePinAssemblySteadyStateSynchronousResponse]: 'FlexiblePinAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FlexiblePinAssemblies, constructor.new(_3294.FlexiblePinAssemblySteadyStateSynchronousResponse))
        return value

    @property
    def hypoid_gear_sets(self) -> 'List[_3300.HypoidGearSetSteadyStateSynchronousResponse]':
        '''List[HypoidGearSetSteadyStateSynchronousResponse]: 'HypoidGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearSets, constructor.new(_3300.HypoidGearSetSteadyStateSynchronousResponse))
        return value

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_sets(self) -> 'List[_3307.KlingelnbergCycloPalloidHypoidGearSetSteadyStateSynchronousResponse]':
        '''List[KlingelnbergCycloPalloidHypoidGearSetSteadyStateSynchronousResponse]: 'KlingelnbergCycloPalloidHypoidGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidGearSets, constructor.new(_3307.KlingelnbergCycloPalloidHypoidGearSetSteadyStateSynchronousResponse))
        return value

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_sets(self) -> 'List[_3310.KlingelnbergCycloPalloidSpiralBevelGearSetSteadyStateSynchronousResponse]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearSetSteadyStateSynchronousResponse]: 'KlingelnbergCycloPalloidSpiralBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelGearSets, constructor.new(_3310.KlingelnbergCycloPalloidSpiralBevelGearSetSteadyStateSynchronousResponse))
        return value

    @property
    def mass_discs(self) -> 'List[_3312.MassDiscSteadyStateSynchronousResponse]':
        '''List[MassDiscSteadyStateSynchronousResponse]: 'MassDiscs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MassDiscs, constructor.new(_3312.MassDiscSteadyStateSynchronousResponse))
        return value

    @property
    def measurement_components(self) -> 'List[_3313.MeasurementComponentSteadyStateSynchronousResponse]':
        '''List[MeasurementComponentSteadyStateSynchronousResponse]: 'MeasurementComponents' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeasurementComponents, constructor.new(_3313.MeasurementComponentSteadyStateSynchronousResponse))
        return value

    @property
    def oil_seals(self) -> 'List[_3315.OilSealSteadyStateSynchronousResponse]':
        '''List[OilSealSteadyStateSynchronousResponse]: 'OilSeals' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.OilSeals, constructor.new(_3315.OilSealSteadyStateSynchronousResponse))
        return value

    @property
    def part_to_part_shear_couplings(self) -> 'List[_3319.PartToPartShearCouplingSteadyStateSynchronousResponse]':
        '''List[PartToPartShearCouplingSteadyStateSynchronousResponse]: 'PartToPartShearCouplings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PartToPartShearCouplings, constructor.new(_3319.PartToPartShearCouplingSteadyStateSynchronousResponse))
        return value

    @property
    def planet_carriers(self) -> 'List[_3322.PlanetCarrierSteadyStateSynchronousResponse]':
        '''List[PlanetCarrierSteadyStateSynchronousResponse]: 'PlanetCarriers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PlanetCarriers, constructor.new(_3322.PlanetCarrierSteadyStateSynchronousResponse))
        return value

    @property
    def point_loads(self) -> 'List[_3323.PointLoadSteadyStateSynchronousResponse]':
        '''List[PointLoadSteadyStateSynchronousResponse]: 'PointLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PointLoads, constructor.new(_3323.PointLoadSteadyStateSynchronousResponse))
        return value

    @property
    def power_loads(self) -> 'List[_3324.PowerLoadSteadyStateSynchronousResponse]':
        '''List[PowerLoadSteadyStateSynchronousResponse]: 'PowerLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PowerLoads, constructor.new(_3324.PowerLoadSteadyStateSynchronousResponse))
        return value

    @property
    def shaft_hub_connections(self) -> 'List[_3332.ShaftHubConnectionSteadyStateSynchronousResponse]':
        '''List[ShaftHubConnectionSteadyStateSynchronousResponse]: 'ShaftHubConnections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ShaftHubConnections, constructor.new(_3332.ShaftHubConnectionSteadyStateSynchronousResponse))
        return value

    @property
    def ring_pins(self) -> 'List[_3326.RingPinsSteadyStateSynchronousResponse]':
        '''List[RingPinsSteadyStateSynchronousResponse]: 'RingPins' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RingPins, constructor.new(_3326.RingPinsSteadyStateSynchronousResponse))
        return value

    @property
    def rolling_ring_assemblies(self) -> 'List[_3328.RollingRingAssemblySteadyStateSynchronousResponse]':
        '''List[RollingRingAssemblySteadyStateSynchronousResponse]: 'RollingRingAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RollingRingAssemblies, constructor.new(_3328.RollingRingAssemblySteadyStateSynchronousResponse))
        return value

    @property
    def shafts(self) -> 'List[_3333.ShaftSteadyStateSynchronousResponse]':
        '''List[ShaftSteadyStateSynchronousResponse]: 'Shafts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Shafts, constructor.new(_3333.ShaftSteadyStateSynchronousResponse))
        return value

    @property
    def spiral_bevel_gear_sets(self) -> 'List[_3337.SpiralBevelGearSetSteadyStateSynchronousResponse]':
        '''List[SpiralBevelGearSetSteadyStateSynchronousResponse]: 'SpiralBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelGearSets, constructor.new(_3337.SpiralBevelGearSetSteadyStateSynchronousResponse))
        return value

    @property
    def spring_dampers(self) -> 'List[_3341.SpringDamperSteadyStateSynchronousResponse]':
        '''List[SpringDamperSteadyStateSynchronousResponse]: 'SpringDampers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpringDampers, constructor.new(_3341.SpringDamperSteadyStateSynchronousResponse))
        return value

    @property
    def straight_bevel_diff_gear_sets(self) -> 'List[_3346.StraightBevelDiffGearSetSteadyStateSynchronousResponse]':
        '''List[StraightBevelDiffGearSetSteadyStateSynchronousResponse]: 'StraightBevelDiffGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffGearSets, constructor.new(_3346.StraightBevelDiffGearSetSteadyStateSynchronousResponse))
        return value

    @property
    def straight_bevel_gear_sets(self) -> 'List[_3349.StraightBevelGearSetSteadyStateSynchronousResponse]':
        '''List[StraightBevelGearSetSteadyStateSynchronousResponse]: 'StraightBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelGearSets, constructor.new(_3349.StraightBevelGearSetSteadyStateSynchronousResponse))
        return value

    @property
    def synchronisers(self) -> 'List[_3356.SynchroniserSteadyStateSynchronousResponse]':
        '''List[SynchroniserSteadyStateSynchronousResponse]: 'Synchronisers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Synchronisers, constructor.new(_3356.SynchroniserSteadyStateSynchronousResponse))
        return value

    @property
    def torque_converters(self) -> 'List[_3359.TorqueConverterSteadyStateSynchronousResponse]':
        '''List[TorqueConverterSteadyStateSynchronousResponse]: 'TorqueConverters' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.TorqueConverters, constructor.new(_3359.TorqueConverterSteadyStateSynchronousResponse))
        return value

    @property
    def unbalanced_masses(self) -> 'List[_3361.UnbalancedMassSteadyStateSynchronousResponse]':
        '''List[UnbalancedMassSteadyStateSynchronousResponse]: 'UnbalancedMasses' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.UnbalancedMasses, constructor.new(_3361.UnbalancedMassSteadyStateSynchronousResponse))
        return value

    @property
    def worm_gear_sets(self) -> 'List[_3364.WormGearSetSteadyStateSynchronousResponse]':
        '''List[WormGearSetSteadyStateSynchronousResponse]: 'WormGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearSets, constructor.new(_3364.WormGearSetSteadyStateSynchronousResponse))
        return value

    @property
    def zerol_bevel_gear_sets(self) -> 'List[_3367.ZerolBevelGearSetSteadyStateSynchronousResponse]':
        '''List[ZerolBevelGearSetSteadyStateSynchronousResponse]: 'ZerolBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelGearSets, constructor.new(_3367.ZerolBevelGearSetSteadyStateSynchronousResponse))
        return value
