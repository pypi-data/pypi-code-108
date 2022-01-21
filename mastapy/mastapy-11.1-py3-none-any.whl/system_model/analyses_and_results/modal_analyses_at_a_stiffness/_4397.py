'''_4397.py

RollingRingModalAnalysisAtAStiffness
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2336
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6665
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness import _4341
from mastapy._internal.python_net import python_net_import

_ROLLING_RING_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness', 'RollingRingModalAnalysisAtAStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('RollingRingModalAnalysisAtAStiffness',)


class RollingRingModalAnalysisAtAStiffness(_4341.CouplingHalfModalAnalysisAtAStiffness):
    '''RollingRingModalAnalysisAtAStiffness

    This is a mastapy class.
    '''

    TYPE = _ROLLING_RING_MODAL_ANALYSIS_AT_A_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollingRingModalAnalysisAtAStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2336.RollingRing':
        '''RollingRing: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2336.RollingRing)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6665.RollingRingLoadCase':
        '''RollingRingLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6665.RollingRingLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def planetaries(self) -> 'List[RollingRingModalAnalysisAtAStiffness]':
        '''List[RollingRingModalAnalysisAtAStiffness]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(RollingRingModalAnalysisAtAStiffness))
        return value
