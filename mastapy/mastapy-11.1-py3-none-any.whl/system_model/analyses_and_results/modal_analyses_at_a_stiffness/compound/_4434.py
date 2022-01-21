'''_4434.py

AbstractShaftCompoundModalAnalysisAtAStiffness
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness import _4304
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import _4435
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness.Compound', 'AbstractShaftCompoundModalAnalysisAtAStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftCompoundModalAnalysisAtAStiffness',)


class AbstractShaftCompoundModalAnalysisAtAStiffness(_4435.AbstractShaftOrHousingCompoundModalAnalysisAtAStiffness):
    '''AbstractShaftCompoundModalAnalysisAtAStiffness

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftCompoundModalAnalysisAtAStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_4304.AbstractShaftModalAnalysisAtAStiffness]':
        '''List[AbstractShaftModalAnalysisAtAStiffness]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4304.AbstractShaftModalAnalysisAtAStiffness))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4304.AbstractShaftModalAnalysisAtAStiffness]':
        '''List[AbstractShaftModalAnalysisAtAStiffness]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4304.AbstractShaftModalAnalysisAtAStiffness))
        return value
