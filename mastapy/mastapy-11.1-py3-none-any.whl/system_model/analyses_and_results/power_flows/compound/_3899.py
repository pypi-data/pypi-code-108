'''_3899.py

AbstractShaftCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.analyses_and_results.power_flows import _3767
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows.compound import _3900
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'AbstractShaftCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftCompoundPowerFlow',)


class AbstractShaftCompoundPowerFlow(_3900.AbstractShaftOrHousingCompoundPowerFlow):
    '''AbstractShaftCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_3767.AbstractShaftPowerFlow]':
        '''List[AbstractShaftPowerFlow]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3767.AbstractShaftPowerFlow))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_3767.AbstractShaftPowerFlow]':
        '''List[AbstractShaftPowerFlow]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3767.AbstractShaftPowerFlow))
        return value
