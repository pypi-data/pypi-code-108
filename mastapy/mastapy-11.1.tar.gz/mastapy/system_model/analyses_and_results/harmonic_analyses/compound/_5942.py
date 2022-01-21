'''_5942.py

PowerLoadCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2213
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5775
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5977
from mastapy._internal.python_net import python_net_import

_POWER_LOAD_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'PowerLoadCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('PowerLoadCompoundHarmonicAnalysis',)


class PowerLoadCompoundHarmonicAnalysis(_5977.VirtualComponentCompoundHarmonicAnalysis):
    '''PowerLoadCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _POWER_LOAD_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PowerLoadCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2213.PowerLoad':
        '''PowerLoad: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2213.PowerLoad)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_5775.PowerLoadHarmonicAnalysis]':
        '''List[PowerLoadHarmonicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5775.PowerLoadHarmonicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_5775.PowerLoadHarmonicAnalysis]':
        '''List[PowerLoadHarmonicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5775.PowerLoadHarmonicAnalysis))
        return value
