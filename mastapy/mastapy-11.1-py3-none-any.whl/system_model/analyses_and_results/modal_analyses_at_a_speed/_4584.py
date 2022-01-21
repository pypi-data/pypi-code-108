'''_4584.py

ClutchHalfModalAnalysisAtASpeed
'''


from mastapy.system_model.part_model.couplings import _2319
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6548
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4600
from mastapy._internal.python_net import python_net_import

_CLUTCH_HALF_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed', 'ClutchHalfModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('ClutchHalfModalAnalysisAtASpeed',)


class ClutchHalfModalAnalysisAtASpeed(_4600.CouplingHalfModalAnalysisAtASpeed):
    '''ClutchHalfModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _CLUTCH_HALF_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ClutchHalfModalAnalysisAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2319.ClutchHalf':
        '''ClutchHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2319.ClutchHalf)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6548.ClutchHalfLoadCase':
        '''ClutchHalfLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6548.ClutchHalfLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
