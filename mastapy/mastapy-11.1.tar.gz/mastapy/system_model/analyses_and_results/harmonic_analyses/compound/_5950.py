'''_5950.py

ShaftCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.part_model.shaft_model import _2223
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5783
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5856
from mastapy._internal.python_net import python_net_import

_SHAFT_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'ShaftCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftCompoundHarmonicAnalysis',)


class ShaftCompoundHarmonicAnalysis(_5856.AbstractShaftCompoundHarmonicAnalysis):
    '''ShaftCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _SHAFT_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2223.Shaft':
        '''Shaft: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2223.Shaft)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_5783.ShaftHarmonicAnalysis]':
        '''List[ShaftHarmonicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5783.ShaftHarmonicAnalysis))
        return value

    @property
    def planetaries(self) -> 'List[ShaftCompoundHarmonicAnalysis]':
        '''List[ShaftCompoundHarmonicAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ShaftCompoundHarmonicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_5783.ShaftHarmonicAnalysis]':
        '''List[ShaftHarmonicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5783.ShaftHarmonicAnalysis))
        return value
