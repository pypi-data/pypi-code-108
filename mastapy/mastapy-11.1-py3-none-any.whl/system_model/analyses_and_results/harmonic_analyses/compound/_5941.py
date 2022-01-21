'''_5941.py

PointLoadCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2212
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5774
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5977
from mastapy._internal.python_net import python_net_import

_POINT_LOAD_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'PointLoadCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('PointLoadCompoundHarmonicAnalysis',)


class PointLoadCompoundHarmonicAnalysis(_5977.VirtualComponentCompoundHarmonicAnalysis):
    '''PointLoadCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _POINT_LOAD_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PointLoadCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2212.PointLoad':
        '''PointLoad: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2212.PointLoad)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_5774.PointLoadHarmonicAnalysis]':
        '''List[PointLoadHarmonicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5774.PointLoadHarmonicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_5774.PointLoadHarmonicAnalysis]':
        '''List[PointLoadHarmonicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5774.PointLoadHarmonicAnalysis))
        return value
