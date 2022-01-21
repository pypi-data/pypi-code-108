'''_5527.py

WormGearHarmonicAnalysisOfSingleExcitation
'''


from mastapy.system_model.part_model.gears import _2291
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6701
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5461
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation', 'WormGearHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearHarmonicAnalysisOfSingleExcitation',)


class WormGearHarmonicAnalysisOfSingleExcitation(_5461.GearHarmonicAnalysisOfSingleExcitation):
    '''WormGearHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2291.WormGear':
        '''WormGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2291.WormGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6701.WormGearLoadCase':
        '''WormGearLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6701.WormGearLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
