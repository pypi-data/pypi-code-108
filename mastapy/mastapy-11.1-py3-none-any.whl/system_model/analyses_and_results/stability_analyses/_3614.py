'''_3614.py

SynchroniserHalfStabilityAnalysis
'''


from mastapy.system_model.part_model.couplings import _2344
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6686
from mastapy.system_model.analyses_and_results.stability_analyses import _3615
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_HALF_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'SynchroniserHalfStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserHalfStabilityAnalysis',)


class SynchroniserHalfStabilityAnalysis(_3615.SynchroniserPartStabilityAnalysis):
    '''SynchroniserHalfStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_HALF_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserHalfStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2344.SynchroniserHalf':
        '''SynchroniserHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2344.SynchroniserHalf)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6686.SynchroniserHalfLoadCase':
        '''SynchroniserHalfLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6686.SynchroniserHalfLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
