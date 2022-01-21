'''_4472.py

CouplingHalfCompoundModalAnalysisAtAStiffness
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness import _4341
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import _4510
from mastapy._internal.python_net import python_net_import

_COUPLING_HALF_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness.Compound', 'CouplingHalfCompoundModalAnalysisAtAStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('CouplingHalfCompoundModalAnalysisAtAStiffness',)


class CouplingHalfCompoundModalAnalysisAtAStiffness(_4510.MountableComponentCompoundModalAnalysisAtAStiffness):
    '''CouplingHalfCompoundModalAnalysisAtAStiffness

    This is a mastapy class.
    '''

    TYPE = _COUPLING_HALF_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CouplingHalfCompoundModalAnalysisAtAStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_4341.CouplingHalfModalAnalysisAtAStiffness]':
        '''List[CouplingHalfModalAnalysisAtAStiffness]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4341.CouplingHalfModalAnalysisAtAStiffness))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4341.CouplingHalfModalAnalysisAtAStiffness]':
        '''List[CouplingHalfModalAnalysisAtAStiffness]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4341.CouplingHalfModalAnalysisAtAStiffness))
        return value
