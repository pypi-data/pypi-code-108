'''_4522.py

RingPinsCompoundModalAnalysisAtAStiffness
'''


from typing import List

from mastapy.system_model.part_model.cycloidal import _2310
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness import _4393
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import _4510
from mastapy._internal.python_net import python_net_import

_RING_PINS_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness.Compound', 'RingPinsCompoundModalAnalysisAtAStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('RingPinsCompoundModalAnalysisAtAStiffness',)


class RingPinsCompoundModalAnalysisAtAStiffness(_4510.MountableComponentCompoundModalAnalysisAtAStiffness):
    '''RingPinsCompoundModalAnalysisAtAStiffness

    This is a mastapy class.
    '''

    TYPE = _RING_PINS_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RingPinsCompoundModalAnalysisAtAStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2310.RingPins':
        '''RingPins: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2310.RingPins)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4393.RingPinsModalAnalysisAtAStiffness]':
        '''List[RingPinsModalAnalysisAtAStiffness]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4393.RingPinsModalAnalysisAtAStiffness))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4393.RingPinsModalAnalysisAtAStiffness]':
        '''List[RingPinsModalAnalysisAtAStiffness]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4393.RingPinsModalAnalysisAtAStiffness))
        return value
