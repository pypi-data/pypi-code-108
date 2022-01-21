'''_4012.py

SynchroniserHalfCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2344
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows import _3881
from mastapy.system_model.analyses_and_results.power_flows.compound import _4013
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_HALF_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'SynchroniserHalfCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserHalfCompoundPowerFlow',)


class SynchroniserHalfCompoundPowerFlow(_4013.SynchroniserPartCompoundPowerFlow):
    '''SynchroniserHalfCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_HALF_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserHalfCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2344.SynchroniserHalf':
        '''SynchroniserHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2344.SynchroniserHalf)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3881.SynchroniserHalfPowerFlow]':
        '''List[SynchroniserHalfPowerFlow]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3881.SynchroniserHalfPowerFlow))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3881.SynchroniserHalfPowerFlow]':
        '''List[SynchroniserHalfPowerFlow]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3881.SynchroniserHalfPowerFlow))
        return value
