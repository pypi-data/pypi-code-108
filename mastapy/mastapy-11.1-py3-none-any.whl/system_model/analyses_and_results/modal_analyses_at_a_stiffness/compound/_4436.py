'''_4436.py

AbstractShaftToMountableComponentConnectionCompoundModalAnalysisAtAStiffness
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness import _4306
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import _4468
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness.Compound', 'AbstractShaftToMountableComponentConnectionCompoundModalAnalysisAtAStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftToMountableComponentConnectionCompoundModalAnalysisAtAStiffness',)


class AbstractShaftToMountableComponentConnectionCompoundModalAnalysisAtAStiffness(_4468.ConnectionCompoundModalAnalysisAtAStiffness):
    '''AbstractShaftToMountableComponentConnectionCompoundModalAnalysisAtAStiffness

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftToMountableComponentConnectionCompoundModalAnalysisAtAStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_4306.AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness]':
        '''List[AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_4306.AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_4306.AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness]':
        '''List[AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_4306.AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness))
        return value
