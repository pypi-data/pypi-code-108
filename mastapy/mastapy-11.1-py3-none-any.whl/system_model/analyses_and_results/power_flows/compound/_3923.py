'''_3923.py

ComponentCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.analyses_and_results.power_flows import _3790
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows.compound import _3977
from mastapy._internal.python_net import python_net_import

_COMPONENT_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'ComponentCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('ComponentCompoundPowerFlow',)


class ComponentCompoundPowerFlow(_3977.PartCompoundPowerFlow):
    '''ComponentCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _COMPONENT_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ComponentCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_3790.ComponentPowerFlow]':
        '''List[ComponentPowerFlow]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3790.ComponentPowerFlow))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_3790.ComponentPowerFlow]':
        '''List[ComponentPowerFlow]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3790.ComponentPowerFlow))
        return value
