'''_4998.py

ComponentCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses import _4845
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _5052
from mastapy._internal.python_net import python_net_import

_COMPONENT_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'ComponentCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ComponentCompoundModalAnalysis',)


class ComponentCompoundModalAnalysis(_5052.PartCompoundModalAnalysis):
    '''ComponentCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _COMPONENT_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ComponentCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_4845.ComponentModalAnalysis]':
        '''List[ComponentModalAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4845.ComponentModalAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4845.ComponentModalAnalysis]':
        '''List[ComponentModalAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4845.ComponentModalAnalysis))
        return value
