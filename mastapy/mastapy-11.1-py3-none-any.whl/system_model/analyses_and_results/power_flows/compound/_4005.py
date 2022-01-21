'''_4005.py

StraightBevelDiffGearSetCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.part_model.gears import _2286
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows.compound import _4003, _4004, _3916
from mastapy.system_model.analyses_and_results.power_flows import _3875
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_DIFF_GEAR_SET_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'StraightBevelDiffGearSetCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelDiffGearSetCompoundPowerFlow',)


class StraightBevelDiffGearSetCompoundPowerFlow(_3916.BevelGearSetCompoundPowerFlow):
    '''StraightBevelDiffGearSetCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_DIFF_GEAR_SET_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelDiffGearSetCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2286.StraightBevelDiffGearSet':
        '''StraightBevelDiffGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2286.StraightBevelDiffGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2286.StraightBevelDiffGearSet':
        '''StraightBevelDiffGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2286.StraightBevelDiffGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def straight_bevel_diff_gears_compound_power_flow(self) -> 'List[_4003.StraightBevelDiffGearCompoundPowerFlow]':
        '''List[StraightBevelDiffGearCompoundPowerFlow]: 'StraightBevelDiffGearsCompoundPowerFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffGearsCompoundPowerFlow, constructor.new(_4003.StraightBevelDiffGearCompoundPowerFlow))
        return value

    @property
    def straight_bevel_diff_meshes_compound_power_flow(self) -> 'List[_4004.StraightBevelDiffGearMeshCompoundPowerFlow]':
        '''List[StraightBevelDiffGearMeshCompoundPowerFlow]: 'StraightBevelDiffMeshesCompoundPowerFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffMeshesCompoundPowerFlow, constructor.new(_4004.StraightBevelDiffGearMeshCompoundPowerFlow))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_3875.StraightBevelDiffGearSetPowerFlow]':
        '''List[StraightBevelDiffGearSetPowerFlow]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_3875.StraightBevelDiffGearSetPowerFlow))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_3875.StraightBevelDiffGearSetPowerFlow]':
        '''List[StraightBevelDiffGearSetPowerFlow]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_3875.StraightBevelDiffGearSetPowerFlow))
        return value
