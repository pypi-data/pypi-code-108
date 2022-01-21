'''_5573.py

CVTBeltConnectionCompoundHarmonicAnalysisOfSingleExcitation
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5443
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import _5542
from mastapy._internal.python_net import python_net_import

_CVT_BELT_CONNECTION_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation.Compound', 'CVTBeltConnectionCompoundHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTBeltConnectionCompoundHarmonicAnalysisOfSingleExcitation',)


class CVTBeltConnectionCompoundHarmonicAnalysisOfSingleExcitation(_5542.BeltConnectionCompoundHarmonicAnalysisOfSingleExcitation):
    '''CVTBeltConnectionCompoundHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _CVT_BELT_CONNECTION_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTBeltConnectionCompoundHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases_ready(self) -> 'List[_5443.CVTBeltConnectionHarmonicAnalysisOfSingleExcitation]':
        '''List[CVTBeltConnectionHarmonicAnalysisOfSingleExcitation]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_5443.CVTBeltConnectionHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_5443.CVTBeltConnectionHarmonicAnalysisOfSingleExcitation]':
        '''List[CVTBeltConnectionHarmonicAnalysisOfSingleExcitation]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_5443.CVTBeltConnectionHarmonicAnalysisOfSingleExcitation))
        return value
