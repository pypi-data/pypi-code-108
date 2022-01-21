'''_4020.py

VirtualComponentCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.analyses_and_results.power_flows import _3891
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows.compound import _3975
from mastapy._internal.python_net import python_net_import

_VIRTUAL_COMPONENT_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'VirtualComponentCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('VirtualComponentCompoundPowerFlow',)


class VirtualComponentCompoundPowerFlow(_3975.MountableComponentCompoundPowerFlow):
    '''VirtualComponentCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _VIRTUAL_COMPONENT_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'VirtualComponentCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_3891.VirtualComponentPowerFlow]':
        '''List[VirtualComponentPowerFlow]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3891.VirtualComponentPowerFlow))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_3891.VirtualComponentPowerFlow]':
        '''List[VirtualComponentPowerFlow]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3891.VirtualComponentPowerFlow))
        return value
