'''_4181.py

AssemblyCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.analyses_and_results.parametric_study_tools import _4081, _4034
from mastapy._internal import constructor, conversion
from mastapy.system_model.part_model import _2176, _2215
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import (
    _4182, _4184, _4187, _4193,
    _4194, _4195, _4200, _4205,
    _4215, _4217, _4219, _4223,
    _4229, _4230, _4231, _4238,
    _4245, _4248, _4249, _4250,
    _4252, _4254, _4259, _4260,
    _4261, _4270, _4263, _4265,
    _4269, _4275, _4276, _4281,
    _4284, _4287, _4291, _4295,
    _4299, _4302, _4174
)
from mastapy._internal.python_net import python_net_import

_ASSEMBLY_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'AssemblyCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('AssemblyCompoundParametricStudyTool',)


class AssemblyCompoundParametricStudyTool(_4174.AbstractAssemblyCompoundParametricStudyTool):
    '''AssemblyCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _ASSEMBLY_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AssemblyCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def all_duty_cycle_results(self) -> '_4081.DutyCycleResultsForAllComponents':
        '''DutyCycleResultsForAllComponents: 'AllDutyCycleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_4081.DutyCycleResultsForAllComponents)(self.wrapped.AllDutyCycleResults) if self.wrapped.AllDutyCycleResults is not None else None

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
    def assembly_analysis_cases_ready(self) -> 'List[_4034.AssemblyParametricStudyTool]':
        '''List[AssemblyParametricStudyTool]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4034.AssemblyParametricStudyTool))
        return value

    @property
    def bearings(self) -> 'List[_4182.BearingCompoundParametricStudyTool]':
        '''List[BearingCompoundParametricStudyTool]: 'Bearings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Bearings, constructor.new(_4182.BearingCompoundParametricStudyTool))
        return value

    @property
    def belt_drives(self) -> 'List[_4184.BeltDriveCompoundParametricStudyTool]':
        '''List[BeltDriveCompoundParametricStudyTool]: 'BeltDrives' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BeltDrives, constructor.new(_4184.BeltDriveCompoundParametricStudyTool))
        return value

    @property
    def bevel_differential_gear_sets(self) -> 'List[_4187.BevelDifferentialGearSetCompoundParametricStudyTool]':
        '''List[BevelDifferentialGearSetCompoundParametricStudyTool]: 'BevelDifferentialGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialGearSets, constructor.new(_4187.BevelDifferentialGearSetCompoundParametricStudyTool))
        return value

    @property
    def bolts(self) -> 'List[_4193.BoltCompoundParametricStudyTool]':
        '''List[BoltCompoundParametricStudyTool]: 'Bolts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Bolts, constructor.new(_4193.BoltCompoundParametricStudyTool))
        return value

    @property
    def bolted_joints(self) -> 'List[_4194.BoltedJointCompoundParametricStudyTool]':
        '''List[BoltedJointCompoundParametricStudyTool]: 'BoltedJoints' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BoltedJoints, constructor.new(_4194.BoltedJointCompoundParametricStudyTool))
        return value

    @property
    def clutches(self) -> 'List[_4195.ClutchCompoundParametricStudyTool]':
        '''List[ClutchCompoundParametricStudyTool]: 'Clutches' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Clutches, constructor.new(_4195.ClutchCompoundParametricStudyTool))
        return value

    @property
    def concept_couplings(self) -> 'List[_4200.ConceptCouplingCompoundParametricStudyTool]':
        '''List[ConceptCouplingCompoundParametricStudyTool]: 'ConceptCouplings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptCouplings, constructor.new(_4200.ConceptCouplingCompoundParametricStudyTool))
        return value

    @property
    def concept_gear_sets(self) -> 'List[_4205.ConceptGearSetCompoundParametricStudyTool]':
        '''List[ConceptGearSetCompoundParametricStudyTool]: 'ConceptGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptGearSets, constructor.new(_4205.ConceptGearSetCompoundParametricStudyTool))
        return value

    @property
    def cv_ts(self) -> 'List[_4215.CVTCompoundParametricStudyTool]':
        '''List[CVTCompoundParametricStudyTool]: 'CVTs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CVTs, constructor.new(_4215.CVTCompoundParametricStudyTool))
        return value

    @property
    def cycloidal_assemblies(self) -> 'List[_4217.CycloidalAssemblyCompoundParametricStudyTool]':
        '''List[CycloidalAssemblyCompoundParametricStudyTool]: 'CycloidalAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CycloidalAssemblies, constructor.new(_4217.CycloidalAssemblyCompoundParametricStudyTool))
        return value

    @property
    def cycloidal_discs(self) -> 'List[_4219.CycloidalDiscCompoundParametricStudyTool]':
        '''List[CycloidalDiscCompoundParametricStudyTool]: 'CycloidalDiscs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CycloidalDiscs, constructor.new(_4219.CycloidalDiscCompoundParametricStudyTool))
        return value

    @property
    def cylindrical_gear_sets(self) -> 'List[_4223.CylindricalGearSetCompoundParametricStudyTool]':
        '''List[CylindricalGearSetCompoundParametricStudyTool]: 'CylindricalGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGearSets, constructor.new(_4223.CylindricalGearSetCompoundParametricStudyTool))
        return value

    @property
    def face_gear_sets(self) -> 'List[_4229.FaceGearSetCompoundParametricStudyTool]':
        '''List[FaceGearSetCompoundParametricStudyTool]: 'FaceGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearSets, constructor.new(_4229.FaceGearSetCompoundParametricStudyTool))
        return value

    @property
    def fe_parts(self) -> 'List[_4230.FEPartCompoundParametricStudyTool]':
        '''List[FEPartCompoundParametricStudyTool]: 'FEParts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FEParts, constructor.new(_4230.FEPartCompoundParametricStudyTool))
        return value

    @property
    def flexible_pin_assemblies(self) -> 'List[_4231.FlexiblePinAssemblyCompoundParametricStudyTool]':
        '''List[FlexiblePinAssemblyCompoundParametricStudyTool]: 'FlexiblePinAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FlexiblePinAssemblies, constructor.new(_4231.FlexiblePinAssemblyCompoundParametricStudyTool))
        return value

    @property
    def hypoid_gear_sets(self) -> 'List[_4238.HypoidGearSetCompoundParametricStudyTool]':
        '''List[HypoidGearSetCompoundParametricStudyTool]: 'HypoidGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearSets, constructor.new(_4238.HypoidGearSetCompoundParametricStudyTool))
        return value

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_sets(self) -> 'List[_4245.KlingelnbergCycloPalloidHypoidGearSetCompoundParametricStudyTool]':
        '''List[KlingelnbergCycloPalloidHypoidGearSetCompoundParametricStudyTool]: 'KlingelnbergCycloPalloidHypoidGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidGearSets, constructor.new(_4245.KlingelnbergCycloPalloidHypoidGearSetCompoundParametricStudyTool))
        return value

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_sets(self) -> 'List[_4248.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundParametricStudyTool]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearSetCompoundParametricStudyTool]: 'KlingelnbergCycloPalloidSpiralBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelGearSets, constructor.new(_4248.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundParametricStudyTool))
        return value

    @property
    def mass_discs(self) -> 'List[_4249.MassDiscCompoundParametricStudyTool]':
        '''List[MassDiscCompoundParametricStudyTool]: 'MassDiscs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MassDiscs, constructor.new(_4249.MassDiscCompoundParametricStudyTool))
        return value

    @property
    def measurement_components(self) -> 'List[_4250.MeasurementComponentCompoundParametricStudyTool]':
        '''List[MeasurementComponentCompoundParametricStudyTool]: 'MeasurementComponents' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeasurementComponents, constructor.new(_4250.MeasurementComponentCompoundParametricStudyTool))
        return value

    @property
    def oil_seals(self) -> 'List[_4252.OilSealCompoundParametricStudyTool]':
        '''List[OilSealCompoundParametricStudyTool]: 'OilSeals' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.OilSeals, constructor.new(_4252.OilSealCompoundParametricStudyTool))
        return value

    @property
    def part_to_part_shear_couplings(self) -> 'List[_4254.PartToPartShearCouplingCompoundParametricStudyTool]':
        '''List[PartToPartShearCouplingCompoundParametricStudyTool]: 'PartToPartShearCouplings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PartToPartShearCouplings, constructor.new(_4254.PartToPartShearCouplingCompoundParametricStudyTool))
        return value

    @property
    def planet_carriers(self) -> 'List[_4259.PlanetCarrierCompoundParametricStudyTool]':
        '''List[PlanetCarrierCompoundParametricStudyTool]: 'PlanetCarriers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PlanetCarriers, constructor.new(_4259.PlanetCarrierCompoundParametricStudyTool))
        return value

    @property
    def point_loads(self) -> 'List[_4260.PointLoadCompoundParametricStudyTool]':
        '''List[PointLoadCompoundParametricStudyTool]: 'PointLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PointLoads, constructor.new(_4260.PointLoadCompoundParametricStudyTool))
        return value

    @property
    def power_loads(self) -> 'List[_4261.PowerLoadCompoundParametricStudyTool]':
        '''List[PowerLoadCompoundParametricStudyTool]: 'PowerLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PowerLoads, constructor.new(_4261.PowerLoadCompoundParametricStudyTool))
        return value

    @property
    def shaft_hub_connections(self) -> 'List[_4270.ShaftHubConnectionCompoundParametricStudyTool]':
        '''List[ShaftHubConnectionCompoundParametricStudyTool]: 'ShaftHubConnections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ShaftHubConnections, constructor.new(_4270.ShaftHubConnectionCompoundParametricStudyTool))
        return value

    @property
    def ring_pins(self) -> 'List[_4263.RingPinsCompoundParametricStudyTool]':
        '''List[RingPinsCompoundParametricStudyTool]: 'RingPins' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RingPins, constructor.new(_4263.RingPinsCompoundParametricStudyTool))
        return value

    @property
    def rolling_ring_assemblies(self) -> 'List[_4265.RollingRingAssemblyCompoundParametricStudyTool]':
        '''List[RollingRingAssemblyCompoundParametricStudyTool]: 'RollingRingAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RollingRingAssemblies, constructor.new(_4265.RollingRingAssemblyCompoundParametricStudyTool))
        return value

    @property
    def shafts(self) -> 'List[_4269.ShaftCompoundParametricStudyTool]':
        '''List[ShaftCompoundParametricStudyTool]: 'Shafts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Shafts, constructor.new(_4269.ShaftCompoundParametricStudyTool))
        return value

    @property
    def spiral_bevel_gear_sets(self) -> 'List[_4275.SpiralBevelGearSetCompoundParametricStudyTool]':
        '''List[SpiralBevelGearSetCompoundParametricStudyTool]: 'SpiralBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelGearSets, constructor.new(_4275.SpiralBevelGearSetCompoundParametricStudyTool))
        return value

    @property
    def spring_dampers(self) -> 'List[_4276.SpringDamperCompoundParametricStudyTool]':
        '''List[SpringDamperCompoundParametricStudyTool]: 'SpringDampers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpringDampers, constructor.new(_4276.SpringDamperCompoundParametricStudyTool))
        return value

    @property
    def straight_bevel_diff_gear_sets(self) -> 'List[_4281.StraightBevelDiffGearSetCompoundParametricStudyTool]':
        '''List[StraightBevelDiffGearSetCompoundParametricStudyTool]: 'StraightBevelDiffGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffGearSets, constructor.new(_4281.StraightBevelDiffGearSetCompoundParametricStudyTool))
        return value

    @property
    def straight_bevel_gear_sets(self) -> 'List[_4284.StraightBevelGearSetCompoundParametricStudyTool]':
        '''List[StraightBevelGearSetCompoundParametricStudyTool]: 'StraightBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelGearSets, constructor.new(_4284.StraightBevelGearSetCompoundParametricStudyTool))
        return value

    @property
    def synchronisers(self) -> 'List[_4287.SynchroniserCompoundParametricStudyTool]':
        '''List[SynchroniserCompoundParametricStudyTool]: 'Synchronisers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Synchronisers, constructor.new(_4287.SynchroniserCompoundParametricStudyTool))
        return value

    @property
    def torque_converters(self) -> 'List[_4291.TorqueConverterCompoundParametricStudyTool]':
        '''List[TorqueConverterCompoundParametricStudyTool]: 'TorqueConverters' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.TorqueConverters, constructor.new(_4291.TorqueConverterCompoundParametricStudyTool))
        return value

    @property
    def unbalanced_masses(self) -> 'List[_4295.UnbalancedMassCompoundParametricStudyTool]':
        '''List[UnbalancedMassCompoundParametricStudyTool]: 'UnbalancedMasses' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.UnbalancedMasses, constructor.new(_4295.UnbalancedMassCompoundParametricStudyTool))
        return value

    @property
    def worm_gear_sets(self) -> 'List[_4299.WormGearSetCompoundParametricStudyTool]':
        '''List[WormGearSetCompoundParametricStudyTool]: 'WormGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearSets, constructor.new(_4299.WormGearSetCompoundParametricStudyTool))
        return value

    @property
    def zerol_bevel_gear_sets(self) -> 'List[_4302.ZerolBevelGearSetCompoundParametricStudyTool]':
        '''List[ZerolBevelGearSetCompoundParametricStudyTool]: 'ZerolBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelGearSets, constructor.new(_4302.ZerolBevelGearSetCompoundParametricStudyTool))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_4034.AssemblyParametricStudyTool]':
        '''List[AssemblyParametricStudyTool]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4034.AssemblyParametricStudyTool))
        return value
