'''_3977.py

PartCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.analyses_and_results.power_flows import _3845
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.analysis_cases import _7263
from mastapy._internal.python_net import python_net_import

_PART_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'PartCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('PartCompoundPowerFlow',)


class PartCompoundPowerFlow(_7263.PartCompoundAnalysis):
    '''PartCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _PART_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PartCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_3845.PartPowerFlow]':
        '''List[PartPowerFlow]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3845.PartPowerFlow))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_3845.PartPowerFlow]':
        '''List[PartPowerFlow]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3845.PartPowerFlow))
        return value
