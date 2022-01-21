'''_5520.py

SynchroniserSleeveHarmonicAnalysisOfSingleExcitation
'''


from mastapy.system_model.part_model.couplings import _2346
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6689
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5519
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_SLEEVE_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation', 'SynchroniserSleeveHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserSleeveHarmonicAnalysisOfSingleExcitation',)


class SynchroniserSleeveHarmonicAnalysisOfSingleExcitation(_5519.SynchroniserPartHarmonicAnalysisOfSingleExcitation):
    '''SynchroniserSleeveHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_SLEEVE_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserSleeveHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2346.SynchroniserSleeve':
        '''SynchroniserSleeve: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2346.SynchroniserSleeve)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6689.SynchroniserSleeveLoadCase':
        '''SynchroniserSleeveLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6689.SynchroniserSleeveLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
