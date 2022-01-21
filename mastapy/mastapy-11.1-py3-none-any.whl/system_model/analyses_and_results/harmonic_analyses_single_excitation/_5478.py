'''_5478.py

KlingelnbergCycloPalloidSpiralBevelGearSetHarmonicAnalysisOfSingleExcitation
'''


from typing import List

from mastapy.system_model.part_model.gears import _2281
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6637
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5476, _5477, _5472
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_SET_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation', 'KlingelnbergCycloPalloidSpiralBevelGearSetHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidSpiralBevelGearSetHarmonicAnalysisOfSingleExcitation',)


class KlingelnbergCycloPalloidSpiralBevelGearSetHarmonicAnalysisOfSingleExcitation(_5472.KlingelnbergCycloPalloidConicalGearSetHarmonicAnalysisOfSingleExcitation):
    '''KlingelnbergCycloPalloidSpiralBevelGearSetHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_SET_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidSpiralBevelGearSetHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2281.KlingelnbergCycloPalloidSpiralBevelGearSet':
        '''KlingelnbergCycloPalloidSpiralBevelGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2281.KlingelnbergCycloPalloidSpiralBevelGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6637.KlingelnbergCycloPalloidSpiralBevelGearSetLoadCase':
        '''KlingelnbergCycloPalloidSpiralBevelGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6637.KlingelnbergCycloPalloidSpiralBevelGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gears_harmonic_analysis_of_single_excitation(self) -> 'List[_5476.KlingelnbergCycloPalloidSpiralBevelGearHarmonicAnalysisOfSingleExcitation]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearHarmonicAnalysisOfSingleExcitation]: 'KlingelnbergCycloPalloidSpiralBevelGearsHarmonicAnalysisOfSingleExcitation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelGearsHarmonicAnalysisOfSingleExcitation, constructor.new(_5476.KlingelnbergCycloPalloidSpiralBevelGearHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_meshes_harmonic_analysis_of_single_excitation(self) -> 'List[_5477.KlingelnbergCycloPalloidSpiralBevelGearMeshHarmonicAnalysisOfSingleExcitation]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearMeshHarmonicAnalysisOfSingleExcitation]: 'KlingelnbergCycloPalloidSpiralBevelMeshesHarmonicAnalysisOfSingleExcitation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelMeshesHarmonicAnalysisOfSingleExcitation, constructor.new(_5477.KlingelnbergCycloPalloidSpiralBevelGearMeshHarmonicAnalysisOfSingleExcitation))
        return value
