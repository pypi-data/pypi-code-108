'''_6390.py

AbstractShaftCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6259
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6391
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'AbstractShaftCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftCompoundCriticalSpeedAnalysis',)


class AbstractShaftCompoundCriticalSpeedAnalysis(_6391.AbstractShaftOrHousingCompoundCriticalSpeedAnalysis):
    '''AbstractShaftCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_6259.AbstractShaftCriticalSpeedAnalysis]':
        '''List[AbstractShaftCriticalSpeedAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6259.AbstractShaftCriticalSpeedAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_6259.AbstractShaftCriticalSpeedAnalysis]':
        '''List[AbstractShaftCriticalSpeedAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6259.AbstractShaftCriticalSpeedAnalysis))
        return value
