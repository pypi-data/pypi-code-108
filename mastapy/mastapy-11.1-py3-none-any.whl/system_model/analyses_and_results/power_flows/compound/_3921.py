'''_3921.py

ClutchHalfCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2319
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows import _3787
from mastapy.system_model.analyses_and_results.power_flows.compound import _3937
from mastapy._internal.python_net import python_net_import

_CLUTCH_HALF_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'ClutchHalfCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('ClutchHalfCompoundPowerFlow',)


class ClutchHalfCompoundPowerFlow(_3937.CouplingHalfCompoundPowerFlow):
    '''ClutchHalfCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _CLUTCH_HALF_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ClutchHalfCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2319.ClutchHalf':
        '''ClutchHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2319.ClutchHalf)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3787.ClutchHalfPowerFlow]':
        '''List[ClutchHalfPowerFlow]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3787.ClutchHalfPowerFlow))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3787.ClutchHalfPowerFlow]':
        '''List[ClutchHalfPowerFlow]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3787.ClutchHalfPowerFlow))
        return value
