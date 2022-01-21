'''_4019.py

UnbalancedMassCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.part_model import _2218
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows import _3890
from mastapy.system_model.analyses_and_results.power_flows.compound import _4020
from mastapy._internal.python_net import python_net_import

_UNBALANCED_MASS_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'UnbalancedMassCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('UnbalancedMassCompoundPowerFlow',)


class UnbalancedMassCompoundPowerFlow(_4020.VirtualComponentCompoundPowerFlow):
    '''UnbalancedMassCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _UNBALANCED_MASS_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'UnbalancedMassCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2218.UnbalancedMass':
        '''UnbalancedMass: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2218.UnbalancedMass)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3890.UnbalancedMassPowerFlow]':
        '''List[UnbalancedMassPowerFlow]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3890.UnbalancedMassPowerFlow))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3890.UnbalancedMassPowerFlow]':
        '''List[UnbalancedMassPowerFlow]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3890.UnbalancedMassPowerFlow))
        return value
