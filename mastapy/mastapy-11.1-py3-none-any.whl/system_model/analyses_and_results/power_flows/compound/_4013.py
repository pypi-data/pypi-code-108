'''_4013.py

SynchroniserPartCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.analyses_and_results.power_flows import _3882
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows.compound import _3937
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_PART_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'SynchroniserPartCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserPartCompoundPowerFlow',)


class SynchroniserPartCompoundPowerFlow(_3937.CouplingHalfCompoundPowerFlow):
    '''SynchroniserPartCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_PART_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserPartCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_3882.SynchroniserPartPowerFlow]':
        '''List[SynchroniserPartPowerFlow]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3882.SynchroniserPartPowerFlow))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_3882.SynchroniserPartPowerFlow]':
        '''List[SynchroniserPartPowerFlow]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3882.SynchroniserPartPowerFlow))
        return value
