'''_5490.py

PointLoadHarmonicAnalysisOfSingleExcitation
'''


from mastapy.system_model.part_model import _2212
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6656
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5526
from mastapy._internal.python_net import python_net_import

_POINT_LOAD_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation', 'PointLoadHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('PointLoadHarmonicAnalysisOfSingleExcitation',)


class PointLoadHarmonicAnalysisOfSingleExcitation(_5526.VirtualComponentHarmonicAnalysisOfSingleExcitation):
    '''PointLoadHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _POINT_LOAD_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PointLoadHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2212.PointLoad':
        '''PointLoad: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2212.PointLoad)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6656.PointLoadLoadCase':
        '''PointLoadLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6656.PointLoadLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
