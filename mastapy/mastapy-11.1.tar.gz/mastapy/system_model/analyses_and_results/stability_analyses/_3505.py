'''_3505.py

AssemblyStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2176, _2215
from mastapy._internal import constructor, conversion
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.static_loads import _6533, _6666
from mastapy.system_model.analyses_and_results.stability_analyses import (
    _3506, _3508, _3510, _3518,
    _3517, _3521, _3526, _3528,
    _3541, _3542, _3545, _3547,
    _3553, _3555, _3556, _3562,
    _3569, _3572, _3574, _3575,
    _3577, _3581, _3584, _3585,
    _3586, _3594, _3588, _3590,
    _3595, _3599, _3603, _3607,
    _3610, _3617, _3620, _3622,
    _3625, _3628, _3498
)
from mastapy._internal.python_net import python_net_import

_ASSEMBLY_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'AssemblyStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('AssemblyStabilityAnalysis',)


class AssemblyStabilityAnalysis(_3498.AbstractAssemblyStabilityAnalysis):
    '''AssemblyStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _ASSEMBLY_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AssemblyStabilityAnalysis.TYPE'):
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
    def bearings(self) -> 'List[_3506.BearingStabilityAnalysis]':
        '''List[BearingStabilityAnalysis]: 'Bearings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Bearings, constructor.new(_3506.BearingStabilityAnalysis))
        return value

    @property
    def belt_drives(self) -> 'List[_3508.BeltDriveStabilityAnalysis]':
        '''List[BeltDriveStabilityAnalysis]: 'BeltDrives' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BeltDrives, constructor.new(_3508.BeltDriveStabilityAnalysis))
        return value

    @property
    def bevel_differential_gear_sets(self) -> 'List[_3510.BevelDifferentialGearSetStabilityAnalysis]':
        '''List[BevelDifferentialGearSetStabilityAnalysis]: 'BevelDifferentialGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialGearSets, constructor.new(_3510.BevelDifferentialGearSetStabilityAnalysis))
        return value

    @property
    def bolts(self) -> 'List[_3518.BoltStabilityAnalysis]':
        '''List[BoltStabilityAnalysis]: 'Bolts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Bolts, constructor.new(_3518.BoltStabilityAnalysis))
        return value

    @property
    def bolted_joints(self) -> 'List[_3517.BoltedJointStabilityAnalysis]':
        '''List[BoltedJointStabilityAnalysis]: 'BoltedJoints' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BoltedJoints, constructor.new(_3517.BoltedJointStabilityAnalysis))
        return value

    @property
    def clutches(self) -> 'List[_3521.ClutchStabilityAnalysis]':
        '''List[ClutchStabilityAnalysis]: 'Clutches' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Clutches, constructor.new(_3521.ClutchStabilityAnalysis))
        return value

    @property
    def concept_couplings(self) -> 'List[_3526.ConceptCouplingStabilityAnalysis]':
        '''List[ConceptCouplingStabilityAnalysis]: 'ConceptCouplings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptCouplings, constructor.new(_3526.ConceptCouplingStabilityAnalysis))
        return value

    @property
    def concept_gear_sets(self) -> 'List[_3528.ConceptGearSetStabilityAnalysis]':
        '''List[ConceptGearSetStabilityAnalysis]: 'ConceptGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptGearSets, constructor.new(_3528.ConceptGearSetStabilityAnalysis))
        return value

    @property
    def cv_ts(self) -> 'List[_3541.CVTStabilityAnalysis]':
        '''List[CVTStabilityAnalysis]: 'CVTs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CVTs, constructor.new(_3541.CVTStabilityAnalysis))
        return value

    @property
    def cycloidal_assemblies(self) -> 'List[_3542.CycloidalAssemblyStabilityAnalysis]':
        '''List[CycloidalAssemblyStabilityAnalysis]: 'CycloidalAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CycloidalAssemblies, constructor.new(_3542.CycloidalAssemblyStabilityAnalysis))
        return value

    @property
    def cycloidal_discs(self) -> 'List[_3545.CycloidalDiscStabilityAnalysis]':
        '''List[CycloidalDiscStabilityAnalysis]: 'CycloidalDiscs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CycloidalDiscs, constructor.new(_3545.CycloidalDiscStabilityAnalysis))
        return value

    @property
    def cylindrical_gear_sets(self) -> 'List[_3547.CylindricalGearSetStabilityAnalysis]':
        '''List[CylindricalGearSetStabilityAnalysis]: 'CylindricalGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGearSets, constructor.new(_3547.CylindricalGearSetStabilityAnalysis))
        return value

    @property
    def face_gear_sets(self) -> 'List[_3553.FaceGearSetStabilityAnalysis]':
        '''List[FaceGearSetStabilityAnalysis]: 'FaceGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearSets, constructor.new(_3553.FaceGearSetStabilityAnalysis))
        return value

    @property
    def fe_parts(self) -> 'List[_3555.FEPartStabilityAnalysis]':
        '''List[FEPartStabilityAnalysis]: 'FEParts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FEParts, constructor.new(_3555.FEPartStabilityAnalysis))
        return value

    @property
    def flexible_pin_assemblies(self) -> 'List[_3556.FlexiblePinAssemblyStabilityAnalysis]':
        '''List[FlexiblePinAssemblyStabilityAnalysis]: 'FlexiblePinAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FlexiblePinAssemblies, constructor.new(_3556.FlexiblePinAssemblyStabilityAnalysis))
        return value

    @property
    def hypoid_gear_sets(self) -> 'List[_3562.HypoidGearSetStabilityAnalysis]':
        '''List[HypoidGearSetStabilityAnalysis]: 'HypoidGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearSets, constructor.new(_3562.HypoidGearSetStabilityAnalysis))
        return value

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_sets(self) -> 'List[_3569.KlingelnbergCycloPalloidHypoidGearSetStabilityAnalysis]':
        '''List[KlingelnbergCycloPalloidHypoidGearSetStabilityAnalysis]: 'KlingelnbergCycloPalloidHypoidGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidGearSets, constructor.new(_3569.KlingelnbergCycloPalloidHypoidGearSetStabilityAnalysis))
        return value

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_sets(self) -> 'List[_3572.KlingelnbergCycloPalloidSpiralBevelGearSetStabilityAnalysis]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearSetStabilityAnalysis]: 'KlingelnbergCycloPalloidSpiralBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelGearSets, constructor.new(_3572.KlingelnbergCycloPalloidSpiralBevelGearSetStabilityAnalysis))
        return value

    @property
    def mass_discs(self) -> 'List[_3574.MassDiscStabilityAnalysis]':
        '''List[MassDiscStabilityAnalysis]: 'MassDiscs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MassDiscs, constructor.new(_3574.MassDiscStabilityAnalysis))
        return value

    @property
    def measurement_components(self) -> 'List[_3575.MeasurementComponentStabilityAnalysis]':
        '''List[MeasurementComponentStabilityAnalysis]: 'MeasurementComponents' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeasurementComponents, constructor.new(_3575.MeasurementComponentStabilityAnalysis))
        return value

    @property
    def oil_seals(self) -> 'List[_3577.OilSealStabilityAnalysis]':
        '''List[OilSealStabilityAnalysis]: 'OilSeals' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.OilSeals, constructor.new(_3577.OilSealStabilityAnalysis))
        return value

    @property
    def part_to_part_shear_couplings(self) -> 'List[_3581.PartToPartShearCouplingStabilityAnalysis]':
        '''List[PartToPartShearCouplingStabilityAnalysis]: 'PartToPartShearCouplings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PartToPartShearCouplings, constructor.new(_3581.PartToPartShearCouplingStabilityAnalysis))
        return value

    @property
    def planet_carriers(self) -> 'List[_3584.PlanetCarrierStabilityAnalysis]':
        '''List[PlanetCarrierStabilityAnalysis]: 'PlanetCarriers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PlanetCarriers, constructor.new(_3584.PlanetCarrierStabilityAnalysis))
        return value

    @property
    def point_loads(self) -> 'List[_3585.PointLoadStabilityAnalysis]':
        '''List[PointLoadStabilityAnalysis]: 'PointLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PointLoads, constructor.new(_3585.PointLoadStabilityAnalysis))
        return value

    @property
    def power_loads(self) -> 'List[_3586.PowerLoadStabilityAnalysis]':
        '''List[PowerLoadStabilityAnalysis]: 'PowerLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PowerLoads, constructor.new(_3586.PowerLoadStabilityAnalysis))
        return value

    @property
    def shaft_hub_connections(self) -> 'List[_3594.ShaftHubConnectionStabilityAnalysis]':
        '''List[ShaftHubConnectionStabilityAnalysis]: 'ShaftHubConnections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ShaftHubConnections, constructor.new(_3594.ShaftHubConnectionStabilityAnalysis))
        return value

    @property
    def ring_pins(self) -> 'List[_3588.RingPinsStabilityAnalysis]':
        '''List[RingPinsStabilityAnalysis]: 'RingPins' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RingPins, constructor.new(_3588.RingPinsStabilityAnalysis))
        return value

    @property
    def rolling_ring_assemblies(self) -> 'List[_3590.RollingRingAssemblyStabilityAnalysis]':
        '''List[RollingRingAssemblyStabilityAnalysis]: 'RollingRingAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RollingRingAssemblies, constructor.new(_3590.RollingRingAssemblyStabilityAnalysis))
        return value

    @property
    def shafts(self) -> 'List[_3595.ShaftStabilityAnalysis]':
        '''List[ShaftStabilityAnalysis]: 'Shafts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Shafts, constructor.new(_3595.ShaftStabilityAnalysis))
        return value

    @property
    def spiral_bevel_gear_sets(self) -> 'List[_3599.SpiralBevelGearSetStabilityAnalysis]':
        '''List[SpiralBevelGearSetStabilityAnalysis]: 'SpiralBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelGearSets, constructor.new(_3599.SpiralBevelGearSetStabilityAnalysis))
        return value

    @property
    def spring_dampers(self) -> 'List[_3603.SpringDamperStabilityAnalysis]':
        '''List[SpringDamperStabilityAnalysis]: 'SpringDampers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpringDampers, constructor.new(_3603.SpringDamperStabilityAnalysis))
        return value

    @property
    def straight_bevel_diff_gear_sets(self) -> 'List[_3607.StraightBevelDiffGearSetStabilityAnalysis]':
        '''List[StraightBevelDiffGearSetStabilityAnalysis]: 'StraightBevelDiffGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffGearSets, constructor.new(_3607.StraightBevelDiffGearSetStabilityAnalysis))
        return value

    @property
    def straight_bevel_gear_sets(self) -> 'List[_3610.StraightBevelGearSetStabilityAnalysis]':
        '''List[StraightBevelGearSetStabilityAnalysis]: 'StraightBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelGearSets, constructor.new(_3610.StraightBevelGearSetStabilityAnalysis))
        return value

    @property
    def synchronisers(self) -> 'List[_3617.SynchroniserStabilityAnalysis]':
        '''List[SynchroniserStabilityAnalysis]: 'Synchronisers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Synchronisers, constructor.new(_3617.SynchroniserStabilityAnalysis))
        return value

    @property
    def torque_converters(self) -> 'List[_3620.TorqueConverterStabilityAnalysis]':
        '''List[TorqueConverterStabilityAnalysis]: 'TorqueConverters' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.TorqueConverters, constructor.new(_3620.TorqueConverterStabilityAnalysis))
        return value

    @property
    def unbalanced_masses(self) -> 'List[_3622.UnbalancedMassStabilityAnalysis]':
        '''List[UnbalancedMassStabilityAnalysis]: 'UnbalancedMasses' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.UnbalancedMasses, constructor.new(_3622.UnbalancedMassStabilityAnalysis))
        return value

    @property
    def worm_gear_sets(self) -> 'List[_3625.WormGearSetStabilityAnalysis]':
        '''List[WormGearSetStabilityAnalysis]: 'WormGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearSets, constructor.new(_3625.WormGearSetStabilityAnalysis))
        return value

    @property
    def zerol_bevel_gear_sets(self) -> 'List[_3628.ZerolBevelGearSetStabilityAnalysis]':
        '''List[ZerolBevelGearSetStabilityAnalysis]: 'ZerolBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelGearSets, constructor.new(_3628.ZerolBevelGearSetStabilityAnalysis))
        return value
