'''_4489.py

FEPartCompoundModalAnalysisAtAStiffness
'''


from typing import List

from mastapy.system_model.part_model import _2194
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness import _4360
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import _4435
from mastapy._internal.python_net import python_net_import

_FE_PART_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness.Compound', 'FEPartCompoundModalAnalysisAtAStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('FEPartCompoundModalAnalysisAtAStiffness',)


class FEPartCompoundModalAnalysisAtAStiffness(_4435.AbstractShaftOrHousingCompoundModalAnalysisAtAStiffness):
    '''FEPartCompoundModalAnalysisAtAStiffness

    This is a mastapy class.
    '''

    TYPE = _FE_PART_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEPartCompoundModalAnalysisAtAStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2194.FEPart':
        '''FEPart: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2194.FEPart)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4360.FEPartModalAnalysisAtAStiffness]':
        '''List[FEPartModalAnalysisAtAStiffness]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4360.FEPartModalAnalysisAtAStiffness))
        return value

    @property
    def planetaries(self) -> 'List[FEPartCompoundModalAnalysisAtAStiffness]':
        '''List[FEPartCompoundModalAnalysisAtAStiffness]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(FEPartCompoundModalAnalysisAtAStiffness))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4360.FEPartModalAnalysisAtAStiffness]':
        '''List[FEPartModalAnalysisAtAStiffness]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4360.FEPartModalAnalysisAtAStiffness))
        return value
