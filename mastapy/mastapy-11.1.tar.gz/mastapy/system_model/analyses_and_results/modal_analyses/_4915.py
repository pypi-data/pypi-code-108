'''_4915.py

RingPinsModalAnalysis
'''


from mastapy.system_model.part_model.cycloidal import _2310
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6661
from mastapy.system_model.analyses_and_results.system_deflections import _2529
from mastapy.system_model.analyses_and_results.modal_analyses import _4902
from mastapy._internal.python_net import python_net_import

_RING_PINS_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses', 'RingPinsModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('RingPinsModalAnalysis',)


class RingPinsModalAnalysis(_4902.MountableComponentModalAnalysis):
    '''RingPinsModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _RING_PINS_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RingPinsModalAnalysis.TYPE'):
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
    def component_load_case(self) -> '_6661.RingPinsLoadCase':
        '''RingPinsLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6661.RingPinsLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def system_deflection_results(self) -> '_2529.RingPinsSystemDeflection':
        '''RingPinsSystemDeflection: 'SystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2529.RingPinsSystemDeflection)(self.wrapped.SystemDeflectionResults) if self.wrapped.SystemDeflectionResults is not None else None
