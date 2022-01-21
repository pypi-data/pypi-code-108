'''_5062.py

RingPinsCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.part_model.cycloidal import _2310
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses import _4915
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _5050
from mastapy._internal.python_net import python_net_import

_RING_PINS_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'RingPinsCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('RingPinsCompoundModalAnalysis',)


class RingPinsCompoundModalAnalysis(_5050.MountableComponentCompoundModalAnalysis):
    '''RingPinsCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _RING_PINS_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RingPinsCompoundModalAnalysis.TYPE'):
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
    def component_analysis_cases_ready(self) -> 'List[_4915.RingPinsModalAnalysis]':
        '''List[RingPinsModalAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4915.RingPinsModalAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4915.RingPinsModalAnalysis]':
        '''List[RingPinsModalAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4915.RingPinsModalAnalysis))
        return value
