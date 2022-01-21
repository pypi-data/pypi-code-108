'''_5475.py

KlingelnbergCycloPalloidHypoidGearSetHarmonicAnalysisOfSingleExcitation
'''


from typing import List

from mastapy.system_model.part_model.gears import _2279
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6634
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5473, _5474, _5472
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SET_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation', 'KlingelnbergCycloPalloidHypoidGearSetHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidHypoidGearSetHarmonicAnalysisOfSingleExcitation',)


class KlingelnbergCycloPalloidHypoidGearSetHarmonicAnalysisOfSingleExcitation(_5472.KlingelnbergCycloPalloidConicalGearSetHarmonicAnalysisOfSingleExcitation):
    '''KlingelnbergCycloPalloidHypoidGearSetHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SET_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidHypoidGearSetHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2279.KlingelnbergCycloPalloidHypoidGearSet':
        '''KlingelnbergCycloPalloidHypoidGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2279.KlingelnbergCycloPalloidHypoidGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6634.KlingelnbergCycloPalloidHypoidGearSetLoadCase':
        '''KlingelnbergCycloPalloidHypoidGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6634.KlingelnbergCycloPalloidHypoidGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def klingelnberg_cyclo_palloid_hypoid_gears_harmonic_analysis_of_single_excitation(self) -> 'List[_5473.KlingelnbergCycloPalloidHypoidGearHarmonicAnalysisOfSingleExcitation]':
        '''List[KlingelnbergCycloPalloidHypoidGearHarmonicAnalysisOfSingleExcitation]: 'KlingelnbergCycloPalloidHypoidGearsHarmonicAnalysisOfSingleExcitation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidGearsHarmonicAnalysisOfSingleExcitation, constructor.new(_5473.KlingelnbergCycloPalloidHypoidGearHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def klingelnberg_cyclo_palloid_hypoid_meshes_harmonic_analysis_of_single_excitation(self) -> 'List[_5474.KlingelnbergCycloPalloidHypoidGearMeshHarmonicAnalysisOfSingleExcitation]':
        '''List[KlingelnbergCycloPalloidHypoidGearMeshHarmonicAnalysisOfSingleExcitation]: 'KlingelnbergCycloPalloidHypoidMeshesHarmonicAnalysisOfSingleExcitation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidMeshesHarmonicAnalysisOfSingleExcitation, constructor.new(_5474.KlingelnbergCycloPalloidHypoidGearMeshHarmonicAnalysisOfSingleExcitation))
        return value
