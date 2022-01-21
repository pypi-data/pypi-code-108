'''_4976.py

AbstractShaftToMountableComponentConnectionCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses import _4823
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _5008
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'AbstractShaftToMountableComponentConnectionCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftToMountableComponentConnectionCompoundModalAnalysis',)


class AbstractShaftToMountableComponentConnectionCompoundModalAnalysis(_5008.ConnectionCompoundModalAnalysis):
    '''AbstractShaftToMountableComponentConnectionCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftToMountableComponentConnectionCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_4823.AbstractShaftToMountableComponentConnectionModalAnalysis]':
        '''List[AbstractShaftToMountableComponentConnectionModalAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_4823.AbstractShaftToMountableComponentConnectionModalAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_4823.AbstractShaftToMountableComponentConnectionModalAnalysis]':
        '''List[AbstractShaftToMountableComponentConnectionModalAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_4823.AbstractShaftToMountableComponentConnectionModalAnalysis))
        return value
