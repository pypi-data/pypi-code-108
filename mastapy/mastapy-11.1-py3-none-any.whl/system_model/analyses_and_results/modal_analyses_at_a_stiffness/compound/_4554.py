'''_4554.py

UnbalancedMassCompoundModalAnalysisAtAStiffness
'''


from typing import List

from mastapy.system_model.part_model import _2218
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness import _4425
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import _4555
from mastapy._internal.python_net import python_net_import

_UNBALANCED_MASS_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness.Compound', 'UnbalancedMassCompoundModalAnalysisAtAStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('UnbalancedMassCompoundModalAnalysisAtAStiffness',)


class UnbalancedMassCompoundModalAnalysisAtAStiffness(_4555.VirtualComponentCompoundModalAnalysisAtAStiffness):
    '''UnbalancedMassCompoundModalAnalysisAtAStiffness

    This is a mastapy class.
    '''

    TYPE = _UNBALANCED_MASS_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'UnbalancedMassCompoundModalAnalysisAtAStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2218.UnbalancedMass':
        '''UnbalancedMass: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2218.UnbalancedMass)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4425.UnbalancedMassModalAnalysisAtAStiffness]':
        '''List[UnbalancedMassModalAnalysisAtAStiffness]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4425.UnbalancedMassModalAnalysisAtAStiffness))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4425.UnbalancedMassModalAnalysisAtAStiffness]':
        '''List[UnbalancedMassModalAnalysisAtAStiffness]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4425.UnbalancedMassModalAnalysisAtAStiffness))
        return value
