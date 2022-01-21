'''_5969.py

SynchroniserHalfCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2344
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5803
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5970
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_HALF_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'SynchroniserHalfCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserHalfCompoundHarmonicAnalysis',)


class SynchroniserHalfCompoundHarmonicAnalysis(_5970.SynchroniserPartCompoundHarmonicAnalysis):
    '''SynchroniserHalfCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_HALF_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserHalfCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2344.SynchroniserHalf':
        '''SynchroniserHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2344.SynchroniserHalf)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_5803.SynchroniserHalfHarmonicAnalysis]':
        '''List[SynchroniserHalfHarmonicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5803.SynchroniserHalfHarmonicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_5803.SynchroniserHalfHarmonicAnalysis]':
        '''List[SynchroniserHalfHarmonicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5803.SynchroniserHalfHarmonicAnalysis))
        return value
