'''_5947.py

RollingRingCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2336
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5781
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5894
from mastapy._internal.python_net import python_net_import

_ROLLING_RING_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'RollingRingCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('RollingRingCompoundHarmonicAnalysis',)


class RollingRingCompoundHarmonicAnalysis(_5894.CouplingHalfCompoundHarmonicAnalysis):
    '''RollingRingCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _ROLLING_RING_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollingRingCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2336.RollingRing':
        '''RollingRing: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2336.RollingRing)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_5781.RollingRingHarmonicAnalysis]':
        '''List[RollingRingHarmonicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5781.RollingRingHarmonicAnalysis))
        return value

    @property
    def planetaries(self) -> 'List[RollingRingCompoundHarmonicAnalysis]':
        '''List[RollingRingCompoundHarmonicAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(RollingRingCompoundHarmonicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_5781.RollingRingHarmonicAnalysis]':
        '''List[RollingRingHarmonicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5781.RollingRingHarmonicAnalysis))
        return value
