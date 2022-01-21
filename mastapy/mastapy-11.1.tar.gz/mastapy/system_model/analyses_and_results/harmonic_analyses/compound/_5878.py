'''_5878.py

ClutchHalfCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2319
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5685
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5894
from mastapy._internal.python_net import python_net_import

_CLUTCH_HALF_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'ClutchHalfCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ClutchHalfCompoundHarmonicAnalysis',)


class ClutchHalfCompoundHarmonicAnalysis(_5894.CouplingHalfCompoundHarmonicAnalysis):
    '''ClutchHalfCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _CLUTCH_HALF_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ClutchHalfCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2319.ClutchHalf':
        '''ClutchHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2319.ClutchHalf)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_5685.ClutchHalfHarmonicAnalysis]':
        '''List[ClutchHalfHarmonicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5685.ClutchHalfHarmonicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_5685.ClutchHalfHarmonicAnalysis]':
        '''List[ClutchHalfHarmonicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5685.ClutchHalfHarmonicAnalysis))
        return value
