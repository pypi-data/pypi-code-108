'''_4014.py

SynchroniserSleeveCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2346
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows import _3884
from mastapy.system_model.analyses_and_results.power_flows.compound import _4013
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_SLEEVE_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'SynchroniserSleeveCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserSleeveCompoundPowerFlow',)


class SynchroniserSleeveCompoundPowerFlow(_4013.SynchroniserPartCompoundPowerFlow):
    '''SynchroniserSleeveCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_SLEEVE_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserSleeveCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2346.SynchroniserSleeve':
        '''SynchroniserSleeve: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2346.SynchroniserSleeve)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3884.SynchroniserSleevePowerFlow]':
        '''List[SynchroniserSleevePowerFlow]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3884.SynchroniserSleevePowerFlow))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3884.SynchroniserSleevePowerFlow]':
        '''List[SynchroniserSleevePowerFlow]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3884.SynchroniserSleevePowerFlow))
        return value
