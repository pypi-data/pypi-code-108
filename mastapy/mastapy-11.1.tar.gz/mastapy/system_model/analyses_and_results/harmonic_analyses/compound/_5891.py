'''_5891.py

ConnectorCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses import _5700
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5932
from mastapy._internal.python_net import python_net_import

_CONNECTOR_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'ConnectorCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConnectorCompoundHarmonicAnalysis',)


class ConnectorCompoundHarmonicAnalysis(_5932.MountableComponentCompoundHarmonicAnalysis):
    '''ConnectorCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONNECTOR_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConnectorCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_5700.ConnectorHarmonicAnalysis]':
        '''List[ConnectorHarmonicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5700.ConnectorHarmonicAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_5700.ConnectorHarmonicAnalysis]':
        '''List[ConnectorHarmonicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5700.ConnectorHarmonicAnalysis))
        return value
