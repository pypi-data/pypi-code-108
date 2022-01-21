'''_5088.py

SynchroniserPartCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses import _4942
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _5012
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_PART_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'SynchroniserPartCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserPartCompoundModalAnalysis',)


class SynchroniserPartCompoundModalAnalysis(_5012.CouplingHalfCompoundModalAnalysis):
    '''SynchroniserPartCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_PART_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserPartCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_4942.SynchroniserPartModalAnalysis]':
        '''List[SynchroniserPartModalAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4942.SynchroniserPartModalAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4942.SynchroniserPartModalAnalysis]':
        '''List[SynchroniserPartModalAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4942.SynchroniserPartModalAnalysis))
        return value
