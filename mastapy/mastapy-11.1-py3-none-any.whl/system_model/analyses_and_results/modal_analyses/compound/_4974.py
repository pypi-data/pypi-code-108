'''_4974.py

AbstractShaftCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses import _4821
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _4975
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'AbstractShaftCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftCompoundModalAnalysis',)


class AbstractShaftCompoundModalAnalysis(_4975.AbstractShaftOrHousingCompoundModalAnalysis):
    '''AbstractShaftCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_4821.AbstractShaftModalAnalysis]':
        '''List[AbstractShaftModalAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4821.AbstractShaftModalAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4821.AbstractShaftModalAnalysis]':
        '''List[AbstractShaftModalAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4821.AbstractShaftModalAnalysis))
        return value
