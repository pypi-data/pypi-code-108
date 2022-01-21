'''_5530.py

ZerolBevelGearHarmonicAnalysisOfSingleExcitation
'''


from mastapy.system_model.part_model.gears import _2293
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6704
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5419
from mastapy._internal.python_net import python_net_import

_ZEROL_BEVEL_GEAR_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation', 'ZerolBevelGearHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('ZerolBevelGearHarmonicAnalysisOfSingleExcitation',)


class ZerolBevelGearHarmonicAnalysisOfSingleExcitation(_5419.BevelGearHarmonicAnalysisOfSingleExcitation):
    '''ZerolBevelGearHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _ZEROL_BEVEL_GEAR_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ZerolBevelGearHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2293.ZerolBevelGear':
        '''ZerolBevelGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2293.ZerolBevelGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6704.ZerolBevelGearLoadCase':
        '''ZerolBevelGearLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6704.ZerolBevelGearLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
