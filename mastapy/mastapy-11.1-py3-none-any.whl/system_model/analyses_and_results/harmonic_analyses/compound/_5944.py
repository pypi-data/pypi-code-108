'''_5944.py

RingPinsCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.part_model.cycloidal import _2310
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5777
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5932
from mastapy._internal.python_net import python_net_import

_RING_PINS_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'RingPinsCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('RingPinsCompoundHarmonicAnalysis',)


class RingPinsCompoundHarmonicAnalysis(_5932.MountableComponentCompoundHarmonicAnalysis):
    '''RingPinsCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _RING_PINS_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RingPinsCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2310.RingPins':
        '''RingPins: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2310.RingPins)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_5777.RingPinsHarmonicAnalysis]':
        '''List[RingPinsHarmonicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5777.RingPinsHarmonicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_5777.RingPinsHarmonicAnalysis]':
        '''List[RingPinsHarmonicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5777.RingPinsHarmonicAnalysis))
        return value
