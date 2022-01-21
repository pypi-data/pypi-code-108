'''_3959.py

GuideDxfModelCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.part_model import _2196
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows import _3827
from mastapy.system_model.analyses_and_results.power_flows.compound import _3923
from mastapy._internal.python_net import python_net_import

_GUIDE_DXF_MODEL_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'GuideDxfModelCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('GuideDxfModelCompoundPowerFlow',)


class GuideDxfModelCompoundPowerFlow(_3923.ComponentCompoundPowerFlow):
    '''GuideDxfModelCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _GUIDE_DXF_MODEL_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GuideDxfModelCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2196.GuideDxfModel':
        '''GuideDxfModel: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2196.GuideDxfModel)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3827.GuideDxfModelPowerFlow]':
        '''List[GuideDxfModelPowerFlow]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3827.GuideDxfModelPowerFlow))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3827.GuideDxfModelPowerFlow]':
        '''List[GuideDxfModelPowerFlow]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3827.GuideDxfModelPowerFlow))
        return value
