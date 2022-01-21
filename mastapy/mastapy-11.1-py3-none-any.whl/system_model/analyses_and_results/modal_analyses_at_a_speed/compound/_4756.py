'''_4756.py

InterMountableComponentConnectionCompoundModalAnalysisAtASpeed
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4627
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import _4726
from mastapy._internal.python_net import python_net_import

_INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed.Compound', 'InterMountableComponentConnectionCompoundModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('InterMountableComponentConnectionCompoundModalAnalysisAtASpeed',)


class InterMountableComponentConnectionCompoundModalAnalysisAtASpeed(_4726.ConnectionCompoundModalAnalysisAtASpeed):
    '''InterMountableComponentConnectionCompoundModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'InterMountableComponentConnectionCompoundModalAnalysisAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_4627.InterMountableComponentConnectionModalAnalysisAtASpeed]':
        '''List[InterMountableComponentConnectionModalAnalysisAtASpeed]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_4627.InterMountableComponentConnectionModalAnalysisAtASpeed))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_4627.InterMountableComponentConnectionModalAnalysisAtASpeed]':
        '''List[InterMountableComponentConnectionModalAnalysisAtASpeed]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_4627.InterMountableComponentConnectionModalAnalysisAtASpeed))
        return value
