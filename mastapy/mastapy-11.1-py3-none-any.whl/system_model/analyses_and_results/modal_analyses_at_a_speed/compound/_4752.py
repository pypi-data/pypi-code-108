'''_4752.py

GuideDxfModelCompoundModalAnalysisAtASpeed
'''


from typing import List

from mastapy.system_model.part_model import _2196
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4623
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import _4716
from mastapy._internal.python_net import python_net_import

_GUIDE_DXF_MODEL_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed.Compound', 'GuideDxfModelCompoundModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('GuideDxfModelCompoundModalAnalysisAtASpeed',)


class GuideDxfModelCompoundModalAnalysisAtASpeed(_4716.ComponentCompoundModalAnalysisAtASpeed):
    '''GuideDxfModelCompoundModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _GUIDE_DXF_MODEL_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GuideDxfModelCompoundModalAnalysisAtASpeed.TYPE'):
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
    def component_analysis_cases_ready(self) -> 'List[_4623.GuideDxfModelModalAnalysisAtASpeed]':
        '''List[GuideDxfModelModalAnalysisAtASpeed]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4623.GuideDxfModelModalAnalysisAtASpeed))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4623.GuideDxfModelModalAnalysisAtASpeed]':
        '''List[GuideDxfModelModalAnalysisAtASpeed]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4623.GuideDxfModelModalAnalysisAtASpeed))
        return value
