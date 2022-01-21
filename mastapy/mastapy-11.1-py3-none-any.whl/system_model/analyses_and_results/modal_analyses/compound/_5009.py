'''_5009.py

ConnectorCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses import _4856
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _5050
from mastapy._internal.python_net import python_net_import

_CONNECTOR_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'ConnectorCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConnectorCompoundModalAnalysis',)


class ConnectorCompoundModalAnalysis(_5050.MountableComponentCompoundModalAnalysis):
    '''ConnectorCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONNECTOR_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConnectorCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_4856.ConnectorModalAnalysis]':
        '''List[ConnectorModalAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4856.ConnectorModalAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4856.ConnectorModalAnalysis]':
        '''List[ConnectorModalAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4856.ConnectorModalAnalysis))
        return value
