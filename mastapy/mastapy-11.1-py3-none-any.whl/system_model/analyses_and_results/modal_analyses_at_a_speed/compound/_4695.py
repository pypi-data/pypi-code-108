'''_4695.py

AGMAGleasonConicalGearCompoundModalAnalysisAtASpeed
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4567
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import _4723
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed.Compound', 'AGMAGleasonConicalGearCompoundModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearCompoundModalAnalysisAtASpeed',)


class AGMAGleasonConicalGearCompoundModalAnalysisAtASpeed(_4723.ConicalGearCompoundModalAnalysisAtASpeed):
    '''AGMAGleasonConicalGearCompoundModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearCompoundModalAnalysisAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_4567.AGMAGleasonConicalGearModalAnalysisAtASpeed]':
        '''List[AGMAGleasonConicalGearModalAnalysisAtASpeed]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4567.AGMAGleasonConicalGearModalAnalysisAtASpeed))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4567.AGMAGleasonConicalGearModalAnalysisAtASpeed]':
        '''List[AGMAGleasonConicalGearModalAnalysisAtASpeed]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4567.AGMAGleasonConicalGearModalAnalysisAtASpeed))
        return value
