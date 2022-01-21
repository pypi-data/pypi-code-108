'''_3954.py

FEPartCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.part_model import _2194
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows import _3822
from mastapy.system_model.analyses_and_results.power_flows.compound import _3900
from mastapy._internal.python_net import python_net_import

_FE_PART_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'FEPartCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('FEPartCompoundPowerFlow',)


class FEPartCompoundPowerFlow(_3900.AbstractShaftOrHousingCompoundPowerFlow):
    '''FEPartCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _FE_PART_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEPartCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2194.FEPart':
        '''FEPart: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2194.FEPart)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3822.FEPartPowerFlow]':
        '''List[FEPartPowerFlow]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3822.FEPartPowerFlow))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3822.FEPartPowerFlow]':
        '''List[FEPartPowerFlow]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3822.FEPartPowerFlow))
        return value
