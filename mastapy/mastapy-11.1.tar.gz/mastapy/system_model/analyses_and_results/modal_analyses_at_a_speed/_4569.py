'''_4569.py

AssemblyModalAnalysisAtASpeed
'''


from typing import List

from mastapy.system_model.part_model import _2176, _2215
from mastapy._internal import constructor, conversion
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.static_loads import _6533, _6666
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import (
    _4570, _4572, _4575, _4582,
    _4581, _4585, _4590, _4593,
    _4603, _4605, _4607, _4611,
    _4617, _4618, _4619, _4626,
    _4633, _4636, _4637, _4638,
    _4640, _4644, _4647, _4648,
    _4649, _4657, _4651, _4653,
    _4658, _4663, _4666, _4669,
    _4672, _4676, _4680, _4683,
    _4687, _4690, _4562
)
from mastapy._internal.python_net import python_net_import

_ASSEMBLY_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed', 'AssemblyModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('AssemblyModalAnalysisAtASpeed',)


class AssemblyModalAnalysisAtASpeed(_4562.AbstractAssemblyModalAnalysisAtASpeed):
    '''AssemblyModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _ASSEMBLY_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AssemblyModalAnalysisAtASpeed.TYPE'):
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
    def bearings(self) -> 'List[_4570.BearingModalAnalysisAtASpeed]':
        '''List[BearingModalAnalysisAtASpeed]: 'Bearings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Bearings, constructor.new(_4570.BearingModalAnalysisAtASpeed))
        return value

    @property
    def belt_drives(self) -> 'List[_4572.BeltDriveModalAnalysisAtASpeed]':
        '''List[BeltDriveModalAnalysisAtASpeed]: 'BeltDrives' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BeltDrives, constructor.new(_4572.BeltDriveModalAnalysisAtASpeed))
        return value

    @property
    def bevel_differential_gear_sets(self) -> 'List[_4575.BevelDifferentialGearSetModalAnalysisAtASpeed]':
        '''List[BevelDifferentialGearSetModalAnalysisAtASpeed]: 'BevelDifferentialGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialGearSets, constructor.new(_4575.BevelDifferentialGearSetModalAnalysisAtASpeed))
        return value

    @property
    def bolts(self) -> 'List[_4582.BoltModalAnalysisAtASpeed]':
        '''List[BoltModalAnalysisAtASpeed]: 'Bolts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Bolts, constructor.new(_4582.BoltModalAnalysisAtASpeed))
        return value

    @property
    def bolted_joints(self) -> 'List[_4581.BoltedJointModalAnalysisAtASpeed]':
        '''List[BoltedJointModalAnalysisAtASpeed]: 'BoltedJoints' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BoltedJoints, constructor.new(_4581.BoltedJointModalAnalysisAtASpeed))
        return value

    @property
    def clutches(self) -> 'List[_4585.ClutchModalAnalysisAtASpeed]':
        '''List[ClutchModalAnalysisAtASpeed]: 'Clutches' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Clutches, constructor.new(_4585.ClutchModalAnalysisAtASpeed))
        return value

    @property
    def concept_couplings(self) -> 'List[_4590.ConceptCouplingModalAnalysisAtASpeed]':
        '''List[ConceptCouplingModalAnalysisAtASpeed]: 'ConceptCouplings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptCouplings, constructor.new(_4590.ConceptCouplingModalAnalysisAtASpeed))
        return value

    @property
    def concept_gear_sets(self) -> 'List[_4593.ConceptGearSetModalAnalysisAtASpeed]':
        '''List[ConceptGearSetModalAnalysisAtASpeed]: 'ConceptGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptGearSets, constructor.new(_4593.ConceptGearSetModalAnalysisAtASpeed))
        return value

    @property
    def cv_ts(self) -> 'List[_4603.CVTModalAnalysisAtASpeed]':
        '''List[CVTModalAnalysisAtASpeed]: 'CVTs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CVTs, constructor.new(_4603.CVTModalAnalysisAtASpeed))
        return value

    @property
    def cycloidal_assemblies(self) -> 'List[_4605.CycloidalAssemblyModalAnalysisAtASpeed]':
        '''List[CycloidalAssemblyModalAnalysisAtASpeed]: 'CycloidalAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CycloidalAssemblies, constructor.new(_4605.CycloidalAssemblyModalAnalysisAtASpeed))
        return value

    @property
    def cycloidal_discs(self) -> 'List[_4607.CycloidalDiscModalAnalysisAtASpeed]':
        '''List[CycloidalDiscModalAnalysisAtASpeed]: 'CycloidalDiscs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CycloidalDiscs, constructor.new(_4607.CycloidalDiscModalAnalysisAtASpeed))
        return value

    @property
    def cylindrical_gear_sets(self) -> 'List[_4611.CylindricalGearSetModalAnalysisAtASpeed]':
        '''List[CylindricalGearSetModalAnalysisAtASpeed]: 'CylindricalGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGearSets, constructor.new(_4611.CylindricalGearSetModalAnalysisAtASpeed))
        return value

    @property
    def face_gear_sets(self) -> 'List[_4617.FaceGearSetModalAnalysisAtASpeed]':
        '''List[FaceGearSetModalAnalysisAtASpeed]: 'FaceGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearSets, constructor.new(_4617.FaceGearSetModalAnalysisAtASpeed))
        return value

    @property
    def fe_parts(self) -> 'List[_4618.FEPartModalAnalysisAtASpeed]':
        '''List[FEPartModalAnalysisAtASpeed]: 'FEParts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FEParts, constructor.new(_4618.FEPartModalAnalysisAtASpeed))
        return value

    @property
    def flexible_pin_assemblies(self) -> 'List[_4619.FlexiblePinAssemblyModalAnalysisAtASpeed]':
        '''List[FlexiblePinAssemblyModalAnalysisAtASpeed]: 'FlexiblePinAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FlexiblePinAssemblies, constructor.new(_4619.FlexiblePinAssemblyModalAnalysisAtASpeed))
        return value

    @property
    def hypoid_gear_sets(self) -> 'List[_4626.HypoidGearSetModalAnalysisAtASpeed]':
        '''List[HypoidGearSetModalAnalysisAtASpeed]: 'HypoidGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearSets, constructor.new(_4626.HypoidGearSetModalAnalysisAtASpeed))
        return value

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_sets(self) -> 'List[_4633.KlingelnbergCycloPalloidHypoidGearSetModalAnalysisAtASpeed]':
        '''List[KlingelnbergCycloPalloidHypoidGearSetModalAnalysisAtASpeed]: 'KlingelnbergCycloPalloidHypoidGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidGearSets, constructor.new(_4633.KlingelnbergCycloPalloidHypoidGearSetModalAnalysisAtASpeed))
        return value

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_sets(self) -> 'List[_4636.KlingelnbergCycloPalloidSpiralBevelGearSetModalAnalysisAtASpeed]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearSetModalAnalysisAtASpeed]: 'KlingelnbergCycloPalloidSpiralBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelGearSets, constructor.new(_4636.KlingelnbergCycloPalloidSpiralBevelGearSetModalAnalysisAtASpeed))
        return value

    @property
    def mass_discs(self) -> 'List[_4637.MassDiscModalAnalysisAtASpeed]':
        '''List[MassDiscModalAnalysisAtASpeed]: 'MassDiscs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MassDiscs, constructor.new(_4637.MassDiscModalAnalysisAtASpeed))
        return value

    @property
    def measurement_components(self) -> 'List[_4638.MeasurementComponentModalAnalysisAtASpeed]':
        '''List[MeasurementComponentModalAnalysisAtASpeed]: 'MeasurementComponents' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeasurementComponents, constructor.new(_4638.MeasurementComponentModalAnalysisAtASpeed))
        return value

    @property
    def oil_seals(self) -> 'List[_4640.OilSealModalAnalysisAtASpeed]':
        '''List[OilSealModalAnalysisAtASpeed]: 'OilSeals' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.OilSeals, constructor.new(_4640.OilSealModalAnalysisAtASpeed))
        return value

    @property
    def part_to_part_shear_couplings(self) -> 'List[_4644.PartToPartShearCouplingModalAnalysisAtASpeed]':
        '''List[PartToPartShearCouplingModalAnalysisAtASpeed]: 'PartToPartShearCouplings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PartToPartShearCouplings, constructor.new(_4644.PartToPartShearCouplingModalAnalysisAtASpeed))
        return value

    @property
    def planet_carriers(self) -> 'List[_4647.PlanetCarrierModalAnalysisAtASpeed]':
        '''List[PlanetCarrierModalAnalysisAtASpeed]: 'PlanetCarriers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PlanetCarriers, constructor.new(_4647.PlanetCarrierModalAnalysisAtASpeed))
        return value

    @property
    def point_loads(self) -> 'List[_4648.PointLoadModalAnalysisAtASpeed]':
        '''List[PointLoadModalAnalysisAtASpeed]: 'PointLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PointLoads, constructor.new(_4648.PointLoadModalAnalysisAtASpeed))
        return value

    @property
    def power_loads(self) -> 'List[_4649.PowerLoadModalAnalysisAtASpeed]':
        '''List[PowerLoadModalAnalysisAtASpeed]: 'PowerLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PowerLoads, constructor.new(_4649.PowerLoadModalAnalysisAtASpeed))
        return value

    @property
    def shaft_hub_connections(self) -> 'List[_4657.ShaftHubConnectionModalAnalysisAtASpeed]':
        '''List[ShaftHubConnectionModalAnalysisAtASpeed]: 'ShaftHubConnections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ShaftHubConnections, constructor.new(_4657.ShaftHubConnectionModalAnalysisAtASpeed))
        return value

    @property
    def ring_pins(self) -> 'List[_4651.RingPinsModalAnalysisAtASpeed]':
        '''List[RingPinsModalAnalysisAtASpeed]: 'RingPins' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RingPins, constructor.new(_4651.RingPinsModalAnalysisAtASpeed))
        return value

    @property
    def rolling_ring_assemblies(self) -> 'List[_4653.RollingRingAssemblyModalAnalysisAtASpeed]':
        '''List[RollingRingAssemblyModalAnalysisAtASpeed]: 'RollingRingAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RollingRingAssemblies, constructor.new(_4653.RollingRingAssemblyModalAnalysisAtASpeed))
        return value

    @property
    def shafts(self) -> 'List[_4658.ShaftModalAnalysisAtASpeed]':
        '''List[ShaftModalAnalysisAtASpeed]: 'Shafts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Shafts, constructor.new(_4658.ShaftModalAnalysisAtASpeed))
        return value

    @property
    def spiral_bevel_gear_sets(self) -> 'List[_4663.SpiralBevelGearSetModalAnalysisAtASpeed]':
        '''List[SpiralBevelGearSetModalAnalysisAtASpeed]: 'SpiralBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelGearSets, constructor.new(_4663.SpiralBevelGearSetModalAnalysisAtASpeed))
        return value

    @property
    def spring_dampers(self) -> 'List[_4666.SpringDamperModalAnalysisAtASpeed]':
        '''List[SpringDamperModalAnalysisAtASpeed]: 'SpringDampers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpringDampers, constructor.new(_4666.SpringDamperModalAnalysisAtASpeed))
        return value

    @property
    def straight_bevel_diff_gear_sets(self) -> 'List[_4669.StraightBevelDiffGearSetModalAnalysisAtASpeed]':
        '''List[StraightBevelDiffGearSetModalAnalysisAtASpeed]: 'StraightBevelDiffGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffGearSets, constructor.new(_4669.StraightBevelDiffGearSetModalAnalysisAtASpeed))
        return value

    @property
    def straight_bevel_gear_sets(self) -> 'List[_4672.StraightBevelGearSetModalAnalysisAtASpeed]':
        '''List[StraightBevelGearSetModalAnalysisAtASpeed]: 'StraightBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelGearSets, constructor.new(_4672.StraightBevelGearSetModalAnalysisAtASpeed))
        return value

    @property
    def synchronisers(self) -> 'List[_4676.SynchroniserModalAnalysisAtASpeed]':
        '''List[SynchroniserModalAnalysisAtASpeed]: 'Synchronisers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Synchronisers, constructor.new(_4676.SynchroniserModalAnalysisAtASpeed))
        return value

    @property
    def torque_converters(self) -> 'List[_4680.TorqueConverterModalAnalysisAtASpeed]':
        '''List[TorqueConverterModalAnalysisAtASpeed]: 'TorqueConverters' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.TorqueConverters, constructor.new(_4680.TorqueConverterModalAnalysisAtASpeed))
        return value

    @property
    def unbalanced_masses(self) -> 'List[_4683.UnbalancedMassModalAnalysisAtASpeed]':
        '''List[UnbalancedMassModalAnalysisAtASpeed]: 'UnbalancedMasses' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.UnbalancedMasses, constructor.new(_4683.UnbalancedMassModalAnalysisAtASpeed))
        return value

    @property
    def worm_gear_sets(self) -> 'List[_4687.WormGearSetModalAnalysisAtASpeed]':
        '''List[WormGearSetModalAnalysisAtASpeed]: 'WormGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearSets, constructor.new(_4687.WormGearSetModalAnalysisAtASpeed))
        return value

    @property
    def zerol_bevel_gear_sets(self) -> 'List[_4690.ZerolBevelGearSetModalAnalysisAtASpeed]':
        '''List[ZerolBevelGearSetModalAnalysisAtASpeed]: 'ZerolBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelGearSets, constructor.new(_4690.ZerolBevelGearSetModalAnalysisAtASpeed))
        return value
