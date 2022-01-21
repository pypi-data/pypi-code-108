'''_5411.py

BearingHarmonicAnalysisOfSingleExcitation
'''


from typing import List

from mastapy.system_model.part_model import _2182
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6534
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5439
from mastapy._internal.python_net import python_net_import

_BEARING_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation', 'BearingHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingHarmonicAnalysisOfSingleExcitation',)


class BearingHarmonicAnalysisOfSingleExcitation(_5439.ConnectorHarmonicAnalysisOfSingleExcitation):
    '''BearingHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _BEARING_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BearingHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2182.Bearing':
        '''Bearing: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2182.Bearing)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6534.BearingLoadCase':
        '''BearingLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6534.BearingLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def planetaries(self) -> 'List[BearingHarmonicAnalysisOfSingleExcitation]':
        '''List[BearingHarmonicAnalysisOfSingleExcitation]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(BearingHarmonicAnalysisOfSingleExcitation))
        return value
