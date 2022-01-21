'''_5630.py

ShaftToMountableComponentConnectionCompoundHarmonicAnalysisOfSingleExcitation
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5501
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import _5536
from mastapy._internal.python_net import python_net_import

_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation.Compound', 'ShaftToMountableComponentConnectionCompoundHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftToMountableComponentConnectionCompoundHarmonicAnalysisOfSingleExcitation',)


class ShaftToMountableComponentConnectionCompoundHarmonicAnalysisOfSingleExcitation(_5536.AbstractShaftToMountableComponentConnectionCompoundHarmonicAnalysisOfSingleExcitation):
    '''ShaftToMountableComponentConnectionCompoundHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftToMountableComponentConnectionCompoundHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_5501.ShaftToMountableComponentConnectionHarmonicAnalysisOfSingleExcitation]':
        '''List[ShaftToMountableComponentConnectionHarmonicAnalysisOfSingleExcitation]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_5501.ShaftToMountableComponentConnectionHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_5501.ShaftToMountableComponentConnectionHarmonicAnalysisOfSingleExcitation]':
        '''List[ShaftToMountableComponentConnectionHarmonicAnalysisOfSingleExcitation]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_5501.ShaftToMountableComponentConnectionHarmonicAnalysisOfSingleExcitation))
        return value
