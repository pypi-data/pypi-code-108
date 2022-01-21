'''_5951.py

ShaftHubConnectionCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2338
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5784
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5891
from mastapy._internal.python_net import python_net_import

_SHAFT_HUB_CONNECTION_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'ShaftHubConnectionCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftHubConnectionCompoundHarmonicAnalysis',)


class ShaftHubConnectionCompoundHarmonicAnalysis(_5891.ConnectorCompoundHarmonicAnalysis):
    '''ShaftHubConnectionCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _SHAFT_HUB_CONNECTION_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftHubConnectionCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2338.ShaftHubConnection':
        '''ShaftHubConnection: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2338.ShaftHubConnection)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_5784.ShaftHubConnectionHarmonicAnalysis]':
        '''List[ShaftHubConnectionHarmonicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5784.ShaftHubConnectionHarmonicAnalysis))
        return value

    @property
    def planetaries(self) -> 'List[ShaftHubConnectionCompoundHarmonicAnalysis]':
        '''List[ShaftHubConnectionCompoundHarmonicAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ShaftHubConnectionCompoundHarmonicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_5784.ShaftHubConnectionHarmonicAnalysis]':
        '''List[ShaftHubConnectionHarmonicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5784.ShaftHubConnectionHarmonicAnalysis))
        return value
