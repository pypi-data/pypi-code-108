'''_4508.py

MassDiscCompoundModalAnalysisAtAStiffness
'''


from typing import List

from mastapy.system_model.part_model import _2203
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness import _4379
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import _4555
from mastapy._internal.python_net import python_net_import

_MASS_DISC_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness.Compound', 'MassDiscCompoundModalAnalysisAtAStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('MassDiscCompoundModalAnalysisAtAStiffness',)


class MassDiscCompoundModalAnalysisAtAStiffness(_4555.VirtualComponentCompoundModalAnalysisAtAStiffness):
    '''MassDiscCompoundModalAnalysisAtAStiffness

    This is a mastapy class.
    '''

    TYPE = _MASS_DISC_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MassDiscCompoundModalAnalysisAtAStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2203.MassDisc':
        '''MassDisc: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2203.MassDisc)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4379.MassDiscModalAnalysisAtAStiffness]':
        '''List[MassDiscModalAnalysisAtAStiffness]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4379.MassDiscModalAnalysisAtAStiffness))
        return value

    @property
    def planetaries(self) -> 'List[MassDiscCompoundModalAnalysisAtAStiffness]':
        '''List[MassDiscCompoundModalAnalysisAtAStiffness]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(MassDiscCompoundModalAnalysisAtAStiffness))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4379.MassDiscModalAnalysisAtAStiffness]':
        '''List[MassDiscModalAnalysisAtAStiffness]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4379.MassDiscModalAnalysisAtAStiffness))
        return value
