'''_5930.py

MassDiscCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2203
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5762
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5977
from mastapy._internal.python_net import python_net_import

_MASS_DISC_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'MassDiscCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('MassDiscCompoundHarmonicAnalysis',)


class MassDiscCompoundHarmonicAnalysis(_5977.VirtualComponentCompoundHarmonicAnalysis):
    '''MassDiscCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _MASS_DISC_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MassDiscCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2203.MassDisc':
        '''MassDisc: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2203.MassDisc)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_5762.MassDiscHarmonicAnalysis]':
        '''List[MassDiscHarmonicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5762.MassDiscHarmonicAnalysis))
        return value

    @property
    def planetaries(self) -> 'List[MassDiscCompoundHarmonicAnalysis]':
        '''List[MassDiscCompoundHarmonicAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(MassDiscCompoundHarmonicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_5762.MassDiscHarmonicAnalysis]':
        '''List[MassDiscHarmonicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5762.MassDiscHarmonicAnalysis))
        return value
