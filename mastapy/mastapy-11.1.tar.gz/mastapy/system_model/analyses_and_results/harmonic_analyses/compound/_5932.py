'''_5932.py

MountableComponentCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses import _5764
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5880
from mastapy._internal.python_net import python_net_import

_MOUNTABLE_COMPONENT_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'MountableComponentCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('MountableComponentCompoundHarmonicAnalysis',)


class MountableComponentCompoundHarmonicAnalysis(_5880.ComponentCompoundHarmonicAnalysis):
    '''MountableComponentCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _MOUNTABLE_COMPONENT_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MountableComponentCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_5764.MountableComponentHarmonicAnalysis]':
        '''List[MountableComponentHarmonicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5764.MountableComponentHarmonicAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_5764.MountableComponentHarmonicAnalysis]':
        '''List[MountableComponentHarmonicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5764.MountableComponentHarmonicAnalysis))
        return value
