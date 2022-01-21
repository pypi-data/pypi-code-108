'''_5529.py

WormGearSetHarmonicAnalysisOfSingleExcitation
'''


from typing import List

from mastapy.system_model.part_model.gears import _2292
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6703
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5527, _5528, _5463
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_SET_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation', 'WormGearSetHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearSetHarmonicAnalysisOfSingleExcitation',)


class WormGearSetHarmonicAnalysisOfSingleExcitation(_5463.GearSetHarmonicAnalysisOfSingleExcitation):
    '''WormGearSetHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_SET_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearSetHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2292.WormGearSet':
        '''WormGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2292.WormGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6703.WormGearSetLoadCase':
        '''WormGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6703.WormGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def worm_gears_harmonic_analysis_of_single_excitation(self) -> 'List[_5527.WormGearHarmonicAnalysisOfSingleExcitation]':
        '''List[WormGearHarmonicAnalysisOfSingleExcitation]: 'WormGearsHarmonicAnalysisOfSingleExcitation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearsHarmonicAnalysisOfSingleExcitation, constructor.new(_5527.WormGearHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def worm_meshes_harmonic_analysis_of_single_excitation(self) -> 'List[_5528.WormGearMeshHarmonicAnalysisOfSingleExcitation]':
        '''List[WormGearMeshHarmonicAnalysisOfSingleExcitation]: 'WormMeshesHarmonicAnalysisOfSingleExcitation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormMeshesHarmonicAnalysisOfSingleExcitation, constructor.new(_5528.WormGearMeshHarmonicAnalysisOfSingleExcitation))
        return value
