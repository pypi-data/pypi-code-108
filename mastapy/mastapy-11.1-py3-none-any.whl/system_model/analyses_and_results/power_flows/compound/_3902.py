'''_3902.py

AGMAGleasonConicalGearCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.analyses_and_results.power_flows import _3770
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows.compound import _3930
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'AGMAGleasonConicalGearCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearCompoundPowerFlow',)


class AGMAGleasonConicalGearCompoundPowerFlow(_3930.ConicalGearCompoundPowerFlow):
    '''AGMAGleasonConicalGearCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_3770.AGMAGleasonConicalGearPowerFlow]':
        '''List[AGMAGleasonConicalGearPowerFlow]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3770.AGMAGleasonConicalGearPowerFlow))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_3770.AGMAGleasonConicalGearPowerFlow]':
        '''List[AGMAGleasonConicalGearPowerFlow]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3770.AGMAGleasonConicalGearPowerFlow))
        return value
