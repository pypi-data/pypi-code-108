'''_5052.py

PartCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses import _4905
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.analysis_cases import _7263
from mastapy._internal.python_net import python_net_import

_PART_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'PartCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('PartCompoundModalAnalysis',)


class PartCompoundModalAnalysis(_7263.PartCompoundAnalysis):
    '''PartCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _PART_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PartCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_4905.PartModalAnalysis]':
        '''List[PartModalAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4905.PartModalAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4905.PartModalAnalysis]':
        '''List[PartModalAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4905.PartModalAnalysis))
        return value
