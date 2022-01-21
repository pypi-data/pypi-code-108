'''_4707.py

BevelGearCompoundModalAnalysisAtASpeed
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4579
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import _4695
from mastapy._internal.python_net import python_net_import

_BEVEL_GEAR_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed.Compound', 'BevelGearCompoundModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelGearCompoundModalAnalysisAtASpeed',)


class BevelGearCompoundModalAnalysisAtASpeed(_4695.AGMAGleasonConicalGearCompoundModalAnalysisAtASpeed):
    '''BevelGearCompoundModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _BEVEL_GEAR_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelGearCompoundModalAnalysisAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_4579.BevelGearModalAnalysisAtASpeed]':
        '''List[BevelGearModalAnalysisAtASpeed]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4579.BevelGearModalAnalysisAtASpeed))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4579.BevelGearModalAnalysisAtASpeed]':
        '''List[BevelGearModalAnalysisAtASpeed]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4579.BevelGearModalAnalysisAtASpeed))
        return value
