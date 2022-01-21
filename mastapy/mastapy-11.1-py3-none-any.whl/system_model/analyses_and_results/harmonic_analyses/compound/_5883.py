'''_5883.py

ConceptCouplingHalfCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2322
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5691
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5894
from mastapy._internal.python_net import python_net_import

_CONCEPT_COUPLING_HALF_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'ConceptCouplingHalfCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptCouplingHalfCompoundHarmonicAnalysis',)


class ConceptCouplingHalfCompoundHarmonicAnalysis(_5894.CouplingHalfCompoundHarmonicAnalysis):
    '''ConceptCouplingHalfCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_COUPLING_HALF_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptCouplingHalfCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2322.ConceptCouplingHalf':
        '''ConceptCouplingHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2322.ConceptCouplingHalf)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_5691.ConceptCouplingHalfHarmonicAnalysis]':
        '''List[ConceptCouplingHalfHarmonicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5691.ConceptCouplingHalfHarmonicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_5691.ConceptCouplingHalfHarmonicAnalysis]':
        '''List[ConceptCouplingHalfHarmonicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5691.ConceptCouplingHalfHarmonicAnalysis))
        return value
