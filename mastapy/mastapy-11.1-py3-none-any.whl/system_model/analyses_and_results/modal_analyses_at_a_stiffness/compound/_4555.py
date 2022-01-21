'''_4555.py

VirtualComponentCompoundModalAnalysisAtAStiffness
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness import _4426
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import _4510
from mastapy._internal.python_net import python_net_import

_VIRTUAL_COMPONENT_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness.Compound', 'VirtualComponentCompoundModalAnalysisAtAStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('VirtualComponentCompoundModalAnalysisAtAStiffness',)


class VirtualComponentCompoundModalAnalysisAtAStiffness(_4510.MountableComponentCompoundModalAnalysisAtAStiffness):
    '''VirtualComponentCompoundModalAnalysisAtAStiffness

    This is a mastapy class.
    '''

    TYPE = _VIRTUAL_COMPONENT_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'VirtualComponentCompoundModalAnalysisAtAStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_4426.VirtualComponentModalAnalysisAtAStiffness]':
        '''List[VirtualComponentModalAnalysisAtAStiffness]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4426.VirtualComponentModalAnalysisAtAStiffness))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4426.VirtualComponentModalAnalysisAtAStiffness]':
        '''List[VirtualComponentModalAnalysisAtAStiffness]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4426.VirtualComponentModalAnalysisAtAStiffness))
        return value
