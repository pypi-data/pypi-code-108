'''_5538.py

AGMAGleasonConicalGearMeshCompoundHarmonicAnalysisOfSingleExcitation
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5408
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import _5566
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_MESH_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation.Compound', 'AGMAGleasonConicalGearMeshCompoundHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearMeshCompoundHarmonicAnalysisOfSingleExcitation',)


class AGMAGleasonConicalGearMeshCompoundHarmonicAnalysisOfSingleExcitation(_5566.ConicalGearMeshCompoundHarmonicAnalysisOfSingleExcitation):
    '''AGMAGleasonConicalGearMeshCompoundHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_MESH_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearMeshCompoundHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_5408.AGMAGleasonConicalGearMeshHarmonicAnalysisOfSingleExcitation]':
        '''List[AGMAGleasonConicalGearMeshHarmonicAnalysisOfSingleExcitation]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_5408.AGMAGleasonConicalGearMeshHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_5408.AGMAGleasonConicalGearMeshHarmonicAnalysisOfSingleExcitation]':
        '''List[AGMAGleasonConicalGearMeshHarmonicAnalysisOfSingleExcitation]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_5408.AGMAGleasonConicalGearMeshHarmonicAnalysisOfSingleExcitation))
        return value
