'''_4747.py

FEPartCompoundModalAnalysisAtASpeed
'''


from typing import List

from mastapy.system_model.part_model import _2194
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4618
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import _4693
from mastapy._internal.python_net import python_net_import

_FE_PART_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed.Compound', 'FEPartCompoundModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('FEPartCompoundModalAnalysisAtASpeed',)


class FEPartCompoundModalAnalysisAtASpeed(_4693.AbstractShaftOrHousingCompoundModalAnalysisAtASpeed):
    '''FEPartCompoundModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _FE_PART_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEPartCompoundModalAnalysisAtASpeed.TYPE'):
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
    def component_analysis_cases_ready(self) -> 'List[_4618.FEPartModalAnalysisAtASpeed]':
        '''List[FEPartModalAnalysisAtASpeed]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4618.FEPartModalAnalysisAtASpeed))
        return value

    @property
    def planetaries(self) -> 'List[FEPartCompoundModalAnalysisAtASpeed]':
        '''List[FEPartCompoundModalAnalysisAtASpeed]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(FEPartCompoundModalAnalysisAtASpeed))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4618.FEPartModalAnalysisAtASpeed]':
        '''List[FEPartModalAnalysisAtASpeed]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4618.FEPartModalAnalysisAtASpeed))
        return value
