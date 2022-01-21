'''_5890.py

ConnectionCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses import _5699
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.analysis_cases import _7256
from mastapy._internal.python_net import python_net_import

_CONNECTION_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'ConnectionCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConnectionCompoundHarmonicAnalysis',)


class ConnectionCompoundHarmonicAnalysis(_7256.ConnectionCompoundAnalysis):
    '''ConnectionCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONNECTION_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConnectionCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_5699.ConnectionHarmonicAnalysis]':
        '''List[ConnectionHarmonicAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_5699.ConnectionHarmonicAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_5699.ConnectionHarmonicAnalysis]':
        '''List[ConnectionHarmonicAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_5699.ConnectionHarmonicAnalysis))
        return value
