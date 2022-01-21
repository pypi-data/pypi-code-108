'''_6468.py

PartCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6339
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.analysis_cases import _7263
from mastapy._internal.python_net import python_net_import

_PART_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'PartCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('PartCompoundCriticalSpeedAnalysis',)


class PartCompoundCriticalSpeedAnalysis(_7263.PartCompoundAnalysis):
    '''PartCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _PART_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PartCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_6339.PartCriticalSpeedAnalysis]':
        '''List[PartCriticalSpeedAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6339.PartCriticalSpeedAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_6339.PartCriticalSpeedAnalysis]':
        '''List[PartCriticalSpeedAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6339.PartCriticalSpeedAnalysis))
        return value
