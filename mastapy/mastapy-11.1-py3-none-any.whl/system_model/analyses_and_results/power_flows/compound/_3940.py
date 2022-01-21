'''_3940.py

CVTPulleyCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.analyses_and_results.power_flows import _3807
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows.compound import _3986
from mastapy._internal.python_net import python_net_import

_CVT_PULLEY_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'CVTPulleyCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTPulleyCompoundPowerFlow',)


class CVTPulleyCompoundPowerFlow(_3986.PulleyCompoundPowerFlow):
    '''CVTPulleyCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _CVT_PULLEY_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTPulleyCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases_ready(self) -> 'List[_3807.CVTPulleyPowerFlow]':
        '''List[CVTPulleyPowerFlow]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3807.CVTPulleyPowerFlow))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3807.CVTPulleyPowerFlow]':
        '''List[CVTPulleyPowerFlow]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3807.CVTPulleyPowerFlow))
        return value
