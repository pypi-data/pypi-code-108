'''_5459.py

FEPartHarmonicAnalysisOfSingleExcitation
'''


from typing import List

from mastapy.system_model.part_model import _2194
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6602
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5405
from mastapy._internal.python_net import python_net_import

_FE_PART_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation', 'FEPartHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('FEPartHarmonicAnalysisOfSingleExcitation',)


class FEPartHarmonicAnalysisOfSingleExcitation(_5405.AbstractShaftOrHousingHarmonicAnalysisOfSingleExcitation):
    '''FEPartHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _FE_PART_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEPartHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2194.FEPart':
        '''FEPart: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2194.FEPart)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6602.FEPartLoadCase':
        '''FEPartLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6602.FEPartLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def planetaries(self) -> 'List[FEPartHarmonicAnalysisOfSingleExcitation]':
        '''List[FEPartHarmonicAnalysisOfSingleExcitation]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(FEPartHarmonicAnalysisOfSingleExcitation))
        return value
