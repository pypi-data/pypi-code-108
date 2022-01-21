'''_5940.py

PlanetCarrierCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2210
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5773
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5932
from mastapy._internal.python_net import python_net_import

_PLANET_CARRIER_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'PlanetCarrierCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetCarrierCompoundHarmonicAnalysis',)


class PlanetCarrierCompoundHarmonicAnalysis(_5932.MountableComponentCompoundHarmonicAnalysis):
    '''PlanetCarrierCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _PLANET_CARRIER_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetCarrierCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2210.PlanetCarrier':
        '''PlanetCarrier: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2210.PlanetCarrier)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_5773.PlanetCarrierHarmonicAnalysis]':
        '''List[PlanetCarrierHarmonicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5773.PlanetCarrierHarmonicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_5773.PlanetCarrierHarmonicAnalysis]':
        '''List[PlanetCarrierHarmonicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5773.PlanetCarrierHarmonicAnalysis))
        return value
