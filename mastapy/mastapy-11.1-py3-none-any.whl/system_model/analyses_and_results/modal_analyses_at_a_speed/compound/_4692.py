'''_4692.py

AbstractShaftCompoundModalAnalysisAtASpeed
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4563
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import _4693
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed.Compound', 'AbstractShaftCompoundModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftCompoundModalAnalysisAtASpeed',)


class AbstractShaftCompoundModalAnalysisAtASpeed(_4693.AbstractShaftOrHousingCompoundModalAnalysisAtASpeed):
    '''AbstractShaftCompoundModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftCompoundModalAnalysisAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_4563.AbstractShaftModalAnalysisAtASpeed]':
        '''List[AbstractShaftModalAnalysisAtASpeed]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4563.AbstractShaftModalAnalysisAtASpeed))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4563.AbstractShaftModalAnalysisAtASpeed]':
        '''List[AbstractShaftModalAnalysisAtASpeed]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4563.AbstractShaftModalAnalysisAtASpeed))
        return value
